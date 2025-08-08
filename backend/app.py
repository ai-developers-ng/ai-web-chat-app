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

# Configure CORS to support credentials
CORS(app, supports_credentials=True, origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:5001', 'http://127.0.0.1:5001', 'http://localhost:8000', 'http://127.0.0.1:8000'])

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

# Initialize AWS Bedrock client using secure credential management
bedrock_runtime = None
credential_manager = None

try:
    # Initialize credential manager with optional profile
    credential_manager = get_credential_manager(
        profile_name=Config.AWS_PROFILE,
        region_name=Config.AWS_REGION
    )
    
    # Get Bedrock client using secure credentials
    bedrock_runtime = credential_manager.get_bedrock_client()
    
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

def invoke_claude(prompt, system_prompt="You are a helpful AI assistant.", image_data=None, image_media_type=None):
    """Invoke Claude model with the given prompt and optional image data"""
    if not bedrock_runtime:
        return {"error": "AWS Bedrock client not initialized"}
    
    try:
        # Construct message content based on whether an image is provided
        if image_data and image_media_type:
            message_content = [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": image_media_type,
                        "data": image_data,
                    },
                },
                {"type": "text", "text": prompt},
            ]
        else:
            message_content = prompt

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": Config.MAX_TOKENS,
            "temperature": Config.TEMPERATURE,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": message_content
                }
            ],
        }
        
        response = bedrock_runtime.invoke_model(
            modelId=Config.CLAUDE_MODEL_ID,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        return {"response": response_body['content'][0]['text']}
        
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
    
    result = invoke_claude(message, system_prompt)
    
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
            # Read file content
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            prompt = f"Please analyze the following document and provide a comprehensive summary, key points, and insights:\n\n{content}"
            system_prompt = "You are an expert document analyzer. Provide detailed analysis, summaries, and extract key insights from documents."
            
            result = invoke_claude(prompt, system_prompt)
            
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
    
    result = invoke_claude(message, system_prompt)
    
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
    
    if file and Config.allowed_.file(file.filename):
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
            # Read and encode image from saved file
            with open(filepath, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            image_media_type = file.mimetype

            prompt = "Please analyze this image in detail. Describe what you see, including objects, scenery, colors, and any text present."
            system_prompt = "You are an expert image analyst. Provide detailed descriptions and analysis of images, including objects, people, scenes, colors, composition, and artistic elements."
            
            result = invoke_claude(
                prompt,
                system_prompt,
                image_data=image_data,
                image_media_type=image_media_type
            )
            
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
