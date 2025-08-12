import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # AWS Configuration - Now using secure credential management
    AWS_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    AWS_PROFILE = os.getenv('AWS_PROFILE')  # Optional AWS profile name
    
    # Legacy environment variables (deprecated but kept for backward compatibility)
    # These will only be used as a fallback if AWS CLI credentials are not available
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    # Bedrock Model IDs
    # Primary chat / code generation model (Meta Llama 3 instruct)
    LLAMA_MODEL_ID = os.getenv('LLAMA_MODEL_ID', 'meta.llama3-70b-instruct-v1:0')
    TITAN_IMAGE_MODEL_ID = "amazon.titan-image-generator-v2:0"
    TITAN_VISION_MODEL_ID = os.getenv('TITAN_VISION_MODEL_ID', '')  # Optional: Titan multimodal caption model
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///ai_web_app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload Configuration
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
    
    # Chat Configuration
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '1024'))  # Max generation tokens for Llama
    TEMPERATURE = 0.7

    # Textract Async (PDF) Configuration
    TEXTRACT_S3_BUCKET = os.getenv('TEXTRACT_S3_BUCKET', '')
    TEXTRACT_S3_PREFIX = os.getenv('TEXTRACT_S3_PREFIX', 'uploads/textract/')
    TEXTRACT_JOB_POLL_SECONDS = int(os.getenv('TEXTRACT_JOB_POLL_SECONDS', '2'))
    TEXTRACT_JOB_TIMEOUT_SECONDS = int(os.getenv('TEXTRACT_JOB_TIMEOUT_SECONDS', '180'))
    
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
