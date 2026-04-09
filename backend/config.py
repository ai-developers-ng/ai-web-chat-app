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
    
    # Bedrock Model IDs — image & vision (unchanged)
    TITAN_IMAGE_MODEL_ID = "amazon.titan-image-generator-v2:0"
    TITAN_VISION_MODEL_ID = os.getenv('TITAN_VISION_MODEL_ID', '')  # Optional: Titan multimodal caption model

    # Multi-model registry — all text/chat models available via AWS Bedrock
    #
    # Each model ID can be overridden via environment variable so you can
    # paste the exact ID from: python backend/check_models.py
    #
    # Newer Claude models (Sonnet/Opus 4.x) are typically only available
    # through cross-region inference profiles — IDs start with "us." for
    # us-east-1 / us-west-2.  Run check_models.py to confirm what is
    # enabled in your account and region.
    MODELS = {
        "claude-sonnet-4-5": {
            "id": os.getenv(
                'MODEL_ID_CLAUDE_SONNET_45',
                'us.anthropic.claude-sonnet-4-5-20250929-v1:0',
            ),
            "name": "Claude Sonnet 4.5",
            "provider": "anthropic",
        },
        "claude-opus-4-5": {
            "id": os.getenv(
                'MODEL_ID_CLAUDE_OPUS_45',
                'us.anthropic.claude-opus-4-5-20251101-v1:0',
            ),
            "name": "Claude Opus 4.5",
            "provider": "anthropic",
        },
        "llama3-70b": {
            "id": os.getenv(
                'MODEL_ID_LLAMA3_70B',
                'meta.llama3-70b-instruct-v1:0',
            ),
            "name": "Llama 3 70B",
            "provider": "meta",
        },
        "llama3-8b": {
            "id": os.getenv(
                'MODEL_ID_LLAMA3_8B',
                'meta.llama3-8b-instruct-v1:0',
            ),
            "name": "Llama 3 8B",
            "provider": "meta",
        },
        "nova-pro": {
            "id": os.getenv(
                'MODEL_ID_NOVA_PRO',
                'amazon.nova-pro-v1:0',
            ),
            "name": "Amazon Nova Pro",
            "provider": "amazon",
        },
    }
    DEFAULT_CHAT_MODEL = os.getenv('DEFAULT_CHAT_MODEL', 'claude-sonnet-4-5')
    DEFAULT_CODE_MODEL = os.getenv('DEFAULT_CODE_MODEL', 'claude-sonnet-4-5')

    # Legacy — kept so document_analyze helper can still call invoke_llama fallback
    LLAMA_MODEL_ID = os.getenv('LLAMA_MODEL_ID', 'meta.llama3-70b-instruct-v1:0')
    
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
