import os
import json
import base64
import time
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager, login_required, current_user
from flask_migrate import Migrate

from werkzeug.utils import secure_filename
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from config import Config
from models import db, User
from auth import auth_bp
from logs import logs_bp, log_search, log_user_action
from admin import admin_bp
from aws_credentials import get_credential_manager, get_bedrock_client
import logging
from configure_global_pem import configure_global_pem
from docx import Document as DocxDocument
import subprocess
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

# Configure CORS to support credentials - specify exact origins (wildcard not allowed with credentials)
_ALLOWED_ORIGINS = [
    'http://localhost:3000', 'http://127.0.0.1:3000',
    'http://localhost:5001', 'http://127.0.0.1:5001',
    'http://localhost:8000', 'http://127.0.0.1:8000'
]
CORS(
    app,
    supports_credentials=True,
    origins=_ALLOWED_ORIGINS,
    allow_headers=['Content-Type', 'Authorization'],
    expose_headers=['*']
)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(logs_bp, url_prefix='/api/logs')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Create upload directory
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# Create database tables
with app.app_context():
    db.create_all()

# Configure global PEM for Bedrock SSL trust
try:
    configure_global_pem()
    logger.info("Global PEM configured for SSL verification")
except Exception as _e:
    logger.warning(f"Could not configure global PEM: {_e}")

# Initialize AWS Bedrock client using secure credential management
bedrock_runtime = None
credential_manager = None
s3_client = None
rekognition_client = None
textract_client = None

try:
    # Initialize credential manager with optional profile
    credential_manager = get_credential_manager(
        profile_name=Config.AWS_PROFILE,
        region_name=Config.AWS_REGION
    )
    
    # Get Bedrock client using secure credentials
    bedrock_runtime = credential_manager.get_bedrock_client()
    # Additional clients for vision/OCR
    session = credential_manager.get_session()
    s3_client = session.client('s3', region_name=Config.AWS_REGION)
    rekognition_client = session.client('rekognition', region_name=Config.AWS_REGION)
    textract_client = session.client('textract', region_name=Config.AWS_REGION)
    
    # Log credential source for debugging
    cred_info = credential_manager.get_credentials_info()
    logger.info(f"AWS Bedrock client initialized successfully using: {cred_info.get('source', 'Unknown')}")
    logger.info(f"AWS Region: {cred_info.get('region')}")
    logger.info(f"AWS Account: {cred_info.get('account_id', 'Unknown')}")
    
except NoCredentialsError as e:
    logger.error(f"AWS credentials not found: {e}")
    bedrock_runtime = None
except Exception as e:
    logger.error(f"Failed to initialize AWS Bedrock client: {e}")
    bedrock_runtime = None

def invoke_llama(prompt, system_prompt="You are a helpful AI assistant.", image_data=None, image_media_type=None):
    """Invoke Meta Llama 3 instruct model with optional image (multi-modal not yet supported for all variants)."""
    if not bedrock_runtime:
        return {"error": "AWS Bedrock client not initialized"}

    try:
        # Current Bedrock Meta Llama 3 models expect a simple JSON with a 'prompt' key.
        # The previous implementation used a 'messages' structure (Anthropic style) which caused ValidationException.
        # We combine system and user into a single prompt. Optionally we could add special tokens, but plain text works.
        combined_prompt = f"System: {system_prompt}\nUser: {prompt}\nAssistant:"  # trailing 'Assistant:' to guide continuation

        body = {
            "prompt": combined_prompt,
            "max_gen_len": Config.MAX_TOKENS,  # maps to maximum new tokens
            "temperature": Config.TEMPERATURE,
            "top_p": 0.9
        }

        response = bedrock_runtime.invoke_model(
            modelId=Config.LLAMA_MODEL_ID,
            body=json.dumps(body)
        )
        response_body = json.loads(response['body'].read())

        # Meta Llama on Bedrock typically returns either {'generation': '...'} or {'outputs':[{'text':'...'}]}.
        text = response_body.get('generation')
        if not text and 'outputs' in response_body:
            outputs = response_body['outputs']
            if outputs and isinstance(outputs, list):
                first = outputs[0]
                if isinstance(first, dict):
                    text = first.get('text') or first.get('generation')
        if not text:
            # Fallback to stringifying (trim to avoid huge payloads)
            text = json.dumps(response_body)[:10000]

        return {"response": text}
    except ClientError as e:
        logger.error(f"AWS Bedrock error: {e}")
        return {"error": f"AWS Bedrock error: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}

def invoke_titan_image(prompt):
    """Generate image using Titan Image Generator"""
    if not bedrock_runtime:
        return {"error": "AWS Bedrock client not initialized"}
    
    try:
        body = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": prompt,
                "negativeText": "low quality, blurry, distorted"
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "height": 512,
                "width": 512,
                "cfgScale": 8.0,
                "seed": 42
            }
        }
        
        response = bedrock_runtime.invoke_model(
            modelId=Config.TITAN_IMAGE_MODEL_ID,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        image_data = response_body['images'][0]
        
        return {"image": image_data}
        
    except ClientError as e:
        logger.error(f"AWS Bedrock error: {e}")
        return {"error": f"AWS Bedrock error: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}

def try_titan_vision_caption(image_bytes: bytes):
    """Optionally attempt a Titan multimodal caption if model ID is configured. Returns text or None."""
    if not bedrock_runtime or not Config.TITAN_VISION_MODEL_ID:
        return None
    try:
        # Titan multimodal request shape varies; using a generic vision prompt if supported by the configured model ID.
        body = {
            "inputImage": base64.b64encode(image_bytes).decode('utf-8'),
            "taskType": "CAPTION"
        }
        resp = bedrock_runtime.invoke_model(
            modelId=Config.TITAN_VISION_MODEL_ID,
            body=json.dumps(body)
        )
        payload = json.loads(resp['body'].read())
        # Try common fields
        return payload.get('caption') or payload.get('text') or None
    except Exception as _e:
        logger.info(f"Titan vision caption not available/failed: {_e}")
        return None

def analyze_image_with_vision_and_ocr(filepath: str, filename: str, mimetype: str):
    """Use AWS Rekognition and Textract to analyze the image and return a readable summary string.

    Returns a dict with key 'response' for frontend compatibility.
    """
    if not rekognition_client or not textract_client:
        return {"error": "AWS Rekognition/Textract clients not initialized"}

    try:
        with open(filepath, 'rb') as f:
            image_bytes = f.read()

        # Rekognition: labels (objects/scenes)
        labels_resp = rekognition_client.detect_labels(
            Image={'Bytes': image_bytes}, MaxLabels=15, MinConfidence=70
        )
        labels = [
            f"{lbl['Name']} ({lbl.get('Confidence', 0):.1f}%)"
            for lbl in labels_resp.get('Labels', [])
        ]

        # Optional Titan caption (if configured)
        titan_caption = try_titan_vision_caption(image_bytes)

        # Rekognition: text (quick OCR)
        rekog_text_resp = rekognition_client.detect_text(Image={'Bytes': image_bytes})
        rekog_lines = [
            d['DetectedText'] for d in rekog_text_resp.get('TextDetections', [])
            if d.get('Type') == 'LINE'
        ]

        # Textract: more robust OCR
        textract_resp = textract_client.detect_document_text(Document={'Bytes': image_bytes})
        textract_lines = [
            b['Text'] for b in textract_resp.get('Blocks', [])
            if b.get('BlockType') == 'LINE'
        ]

        # Compose a structured summary
        summary_parts = []
        summary_parts.append(f"Image: {filename} ({mimetype})")
        if labels:
            summary_parts.append("Detected labels (objects/scenes):")
            summary_parts.append("- " + "\n- ".join(labels[:10]))
        if titan_caption:
            summary_parts.append("Model caption (Titan):\n" + titan_caption)
        if rekog_lines or textract_lines:
            # Prefer Textract lines when available
            ocr_lines = textract_lines if textract_lines else rekog_lines
            joined = "\n".join(ocr_lines[:25])
            summary_parts.append("Extracted text (OCR):\n" + joined)

        draft_summary = "\n\n".join(summary_parts)

        # Optionally ask Llama to craft a concise human-friendly description
        try:
            llm_prompt = (
                "Given the labels and OCR text below, write a concise description of the image, "
                "mentioning key objects, scene, and any important text.\n\n" + draft_summary
            )
            llm = invoke_llama(llm_prompt, system_prompt=(
                "You are an expert image analyst. Summarize the image content clearly."
            ))
            if isinstance(llm, dict) and llm.get('response'):
                final_text = llm['response']
            else:
                final_text = draft_summary
        except Exception as _e:
            logger.warning(f"LLM summary failed, returning raw summary: {_e}")
            final_text = draft_summary

        return {"response": final_text}
    except ClientError as e:
        logger.error(f"AWS vision/OCR error: {e}")
        return {"error": f"AWS vision/OCR error: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected vision/OCR error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}

def _upload_to_s3(local_path: str, bucket: str, key: str):
    s3_client.upload_file(local_path, bucket, key)
    return f"s3://{bucket}/{key}"

def _start_textract_pdf_job(s3_bucket: str, s3_key: str):
    resp = textract_client.start_document_text_detection(
        DocumentLocation={
            'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}
        }
    )
    return resp['JobId']

def _wait_for_textract_job(job_id: str, poll_seconds: int, timeout_seconds: int):
    start = time.time()
    while True:
        resp = textract_client.get_document_text_detection(JobId=job_id)
        status = resp.get('JobStatus')
        if status in ('SUCCEEDED', 'FAILED', 'PARTIAL_SUCCESS'):  # partial still yields pages
            return status
        if time.time() - start > timeout_seconds:
            raise TimeoutError("Textract job timed out")
        time.sleep(poll_seconds)

def _collect_textract_pages(job_id: str):
    pages = []
    pagination_token = None
    while True:
        kwargs = {'JobId': job_id}
        if pagination_token:
            kwargs['NextToken'] = pagination_token
        resp = textract_client.get_document_text_detection(**kwargs)
        lines = [
            b['Text'] for b in resp.get('Blocks', []) if b.get('BlockType') == 'LINE'
        ]
        pages.append("\n".join(lines))
        pagination_token = resp.get('NextToken')
        if not pagination_token:
            break
    return pages

def _doc_extract_prereqs():
    """Check if system tools needed by textract for .doc are available."""
    antiword = shutil.which('antiword')
    catdoc = shutil.which('catdoc')
    return {
        'antiword': bool(antiword),
        'catdoc': bool(catdoc),
        'supported': bool(antiword or catdoc)
    }

def _extract_doc_with_tool(filepath: str) -> str:
    """Extract text from .doc using antiword or catdoc via subprocess."""
    tools = []
    if shutil.which('antiword'):
        tools.append(['antiword', filepath])
    if shutil.which('catdoc'):
        tools.append(['catdoc', filepath])
    last_err = None
    for cmd in tools:
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            text = out.decode('utf-8', errors='ignore').strip()
            if text:
                return text
        except subprocess.CalledProcessError as e:
            last_err = e.output.decode('utf-8', errors='ignore')
            continue
    if last_err:
        raise RuntimeError(f".doc extraction failed: {last_err}")
    raise RuntimeError("No supported .doc extraction tool available")

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    """General AI chatbot endpoint"""
    start_time = time.time()
    
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Message is required"}), 400
    
    message = data['message']
    system_prompt = "You are a helpful, friendly, and knowledgeable AI assistant. Provide clear, accurate, and helpful responses to user questions."
    
    # Log user action
    log_user_action('chat_request', {'message_length': len(message)})
    
    result = invoke_llama(message, system_prompt)
    
    # Log search
    response_time = time.time() - start_time
    response_text = result.get('response', result.get('error', ''))
    log_search('chat', message, response_text, response_time)
    
    return jsonify(result)

@app.route('/api/document-analyze', methods=['POST'])
@login_required
def document_analyze():
    """Document analyzer endpoint"""
    start_time = time.time()
    
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file and Config.allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Log file upload action
        log_user_action('file_upload', {
            'filename': filename,
            'file_size': os.path.getsize(filepath),
            'file_type': 'document'
        })
        
        try:
            # Choose processing strategy by file type
            ext = os.path.splitext(filename)[1].lower()
            mimetype = file.mimetype

            if ext in ['.png', '.jpg', '.jpeg', '.tif', '.tiff']:
                # Use Rekognition + Textract OCR for scanned documents/images
                result = analyze_image_with_vision_and_ocr(filepath, filename, mimetype)
            elif ext == '.pdf':
                # Textract async PDF OCR via S3
                if not Config.TEXTRACT_S3_BUCKET:
                    result = {
                        'error': (
                            'PDF OCR requires configuring TEXTRACT_S3_BUCKET in backend .env. '
                            'Provide an S3 bucket and permissions for Textract.'
                        )
                    }
                else:
                    # Upload PDF to S3
                    s3_key = f"{Config.TEXTRACT_S3_PREFIX.rstrip('/')}/{int(time.time())}-{secure_filename(filename)}"
                    _upload_to_s3(filepath, Config.TEXTRACT_S3_BUCKET, s3_key)
                    # Start Textract job
                    job_id = _start_textract_pdf_job(Config.TEXTRACT_S3_BUCKET, s3_key)
                    # Poll for completion
                    _wait_for_textract_job(job_id, Config.TEXTRACT_JOB_POLL_SECONDS, Config.TEXTRACT_JOB_TIMEOUT_SECONDS)
                    # Collect pages and summarize
                    pages = _collect_textract_pages(job_id)
                    combined_text = "\n\n".join([f"[Page {i+1}]\n{t}" for i, t in enumerate(pages)])
                    prompt = (
                        "Analyze this PDF content. Provide a concise summary, key points, and any action items.\n\n" + combined_text
                    )
                    system_prompt = "You are an expert document analyst."
                    result = invoke_llama(prompt, system_prompt)
            elif ext in ['.txt', '.md']:
                # Simple text files: read and analyze
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                prompt = (
                    "Please analyze the following document and provide a comprehensive summary, key points, and insights:\n\n"
                    + content
                )
                system_prompt = "You are an expert document analyzer."
                result = invoke_llama(prompt, system_prompt)
            elif ext in ['.docx']:
                # Extract text from DOCX and analyze
                try:
                    doc = DocxDocument(filepath)
                    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
                    content = "\n".join(paragraphs)
                except Exception as _e:
                    result = { 'error': f'Failed to read DOCX: {_e}'}
                else:
                    if not content:
                        result = { 'error': 'DOCX contains no readable text.' }
                    else:
                        prompt = (
                            "Please analyze the following document and provide a comprehensive summary, key points, and insights:\n\n"
                            + content
                        )
                        system_prompt = "You are an expert document analyzer."
                        result = invoke_llama(prompt, system_prompt)
            elif ext in ['.doc']:
                # Extract text from legacy Word (.doc) using antiword/catdoc
                prereq = _doc_extract_prereqs()
                if not prereq['supported']:
                    missing = []
                    if not prereq['antiword']:
                        missing.append('antiword')
                    if not prereq['catdoc']:
                        missing.append('catdoc')
                    result = { 'error': (
                        'DOC extraction prerequisites missing: ' + ', '.join(missing) + '. '
                        'Install one of them (e.g., brew install antiword) and retry.'
                    )}
                else:
                    try:
                        content = _extract_doc_with_tool(filepath)
                    except Exception as _e:
                        result = { 'error': f'Failed to read DOC: {_e}'}
                    else:
                        if not content:
                            result = { 'error': 'DOC contains no readable text.' }
                        else:
                            prompt = (
                                "Please analyze the following document and provide a comprehensive summary, key points, and insights:\n\n"
                                + content
                            )
                            system_prompt = "You are an expert document analyzer."
                            result = invoke_llama(prompt, system_prompt)
            else:
                # Unsupported rich formats without extra deps (doc/docx); advise user
                result = {
                    'error': (
                        'Unsupported file type for OCR in this setup. '
                        'Use PNG/JPG for scans, TXT/MD for text, DOCX for Word docs. PDF OCR requires S3+Textract (async).'
                    )
                }
            
            # Log search
            response_time = time.time() - start_time
            response_text = result.get('response', result.get('error', ''))
            log_search('document', f"Document: {filename}", response_text, response_time)
            
            # Clean up uploaded file
            os.remove(filepath)
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return jsonify({"error": f"Error processing document: {str(e)}"}), 500
    
    return jsonify({"error": "Invalid file type"}), 400

@app.route('/api/code-chat', methods=['POST'])
@login_required
def code_chat():
    """Coding chatbot endpoint"""
    start_time = time.time()
    
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Message is required"}), 400
    
    message = data['message']
    system_prompt = """You are an expert software engineer and coding assistant. Help users with:
    - Writing clean, efficient code
    - Debugging and troubleshooting
    - Code reviews and optimization
    - Best practices and design patterns
    - Explaining complex programming concepts
    
    Always provide clear explanations and well-commented code examples."""
    
    # Log user action
    log_user_action('code_chat_request', {'message_length': len(message)})
    
    result = invoke_llama(message, system_prompt)
    
    # Log search
    response_time = time.time() - start_time
    response_text = result.get('response', result.get('error', ''))
    log_search('code', message, response_text, response_time)
    
    return jsonify(result)

@app.route('/api/generate-image', methods=['POST'])
@login_required
def generate_image():
    """Image generator endpoint"""
    start_time = time.time()
    
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Prompt is required"}), 400
    
    prompt = data['prompt']
    
    # Log user action
    log_user_action('image_generation_request', {'prompt_length': len(prompt)})
    
    result = invoke_titan_image(prompt)
    
    # Log search
    response_time = time.time() - start_time
    response_text = "Image generated successfully" if 'image' in result else result.get('error', '')
    log_search('image_gen', prompt, response_text, response_time)
    
    return jsonify(result)

@app.route('/api/analyze-image', methods=['POST'])
@login_required
def analyze_image():
    """Image analyzer endpoint"""
    start_time = time.time()
    
    if 'file' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file and Config.allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Log file upload action
        log_user_action('file_upload', {
            'filename': filename,
            'file_size': os.path.getsize(filepath),
            'file_type': 'image'
        })
        
        try:
            result = analyze_image_with_vision_and_ocr(filepath, filename, file.mimetype)
            
            # Log search
            response_time = time.time() - start_time
            response_text = result.get('response', result.get('error', ''))
            log_search('image_analyze', f"Image: {filename}", response_text, response_time)
            
            # Clean up uploaded file
            os.remove(filepath)
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return jsonify({"error": f"Error processing image: {str(e)}"}), 500
    
    return jsonify({"error": "Invalid file type"}), 400

@app.errorhandler(413)
def request_entity_too_large(e):
    return jsonify({"error": "File too large"}), 413

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    health_info = {
        "status": "healthy",
        "bedrock_available": bedrock_runtime is not None,
        "database_connected": True,
    "authentication_enabled": True
    }
    
    # Add AWS credential information if available
    if credential_manager:
        try:
            cred_info = credential_manager.get_credentials_info()
            health_info["aws_credentials"] = {
                "source": cred_info.get('source', 'Unknown'),
                "region": cred_info.get('region'),
                "account_id": cred_info.get('account_id', 'Unknown')[:8] + "****" if cred_info.get('account_id') else None,
                "profile": cred_info.get('profile')
            }
        except Exception as e:
            health_info["aws_credentials"] = {"error": str(e)}
    
    # Add document processing capability info
    try:
        prereq = _doc_extract_prereqs()
        health_info["doc_support"] = {
            "docx": True,
            "doc": prereq['supported'],
            "doc_prereqs": prereq,
            "pdf_textract_configured": bool(Config.TEXTRACT_S3_BUCKET)
        }
    except Exception as _e:
        health_info["doc_support_error"] = str(_e)

    return jsonify(health_info)

@app.route('/api/aws-status', methods=['GET'])
@login_required
def aws_status():
    """Detailed AWS status endpoint for authenticated users"""
    if not credential_manager:
        return jsonify({
            "error": "AWS credential manager not initialized"
        }), 500
    
    try:
        # Get credential information
        cred_info = credential_manager.get_credentials_info()
        
        # Test Bedrock access
        bedrock_test = credential_manager.test_bedrock_access()
        
        return jsonify({
            "credentials": {
                "source": cred_info.get('source', 'Unknown'),
                "region": cred_info.get('region'),
                "account_id": cred_info.get('account_id'),
                "user_id": cred_info.get('user_id'),
                "arn": cred_info.get('arn'),
                "profile": cred_info.get('profile')
            },
            "bedrock": bedrock_test
        })
        
    except Exception as e:
        logger.error(f"Error getting AWS status: {e}")
        return jsonify({
            "error": f"Failed to get AWS status: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
