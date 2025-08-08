# AI Web Application with AWS Bedrock

A comprehensive web application featuring multiple AI-powered tools using AWS Bedrock's various models including Claude 3 and Titan Image Generator, with complete user authentication and activity logging.

## Features

🤖 **AI Chatbot** - General purpose conversational AI using Claude 3
📄 **Document Analyzer** - Upload and analyze documents with AI insights
💻 **Coding Assistant** - Specialized AI helper for programming tasks
🎨 **Image Generator** - Create images from text prompts using Titan Image Generator
🔍 **Image Analyzer** - Upload images for AI-powered analysis and description
🔐 **User Authentication** - Secure login/register system with session management
📊 **Activity Logging** - Comprehensive logging of all user actions and AI interactions
📈 **Usage Statistics** - Detailed analytics and history tracking
👤 **User Profiles** - Personal profiles with data export capabilities

## Architecture

- **Frontend**: Modern HTML5, CSS3, and JavaScript with responsive design
- **Backend**: Python Flask API server with SQLAlchemy ORM
- **Database**: SQLite (default) with support for PostgreSQL/MySQL
- **Authentication**: Flask-Login with secure session management
- **AI Models**: AWS Bedrock (Claude 3, Titan Image Generator)
- **File Handling**: Support for documents and images
- **Logging**: Comprehensive activity and usage tracking

## Prerequisites

- Python 3.8 or higher
- AWS Account with Bedrock access
- AWS CLI configured
- Modern web browser

## Quick Start

### Option 1: Automated Setup (Recommended)

**Linux/Mac:**
```bash
cd ai-web-app
chmod +x start.sh
./start.sh
```

**Windows:**
```batch
cd ai-web-app
start.bat
```

The automated setup will:
- Install Python dependencies
- Initialize the database with default admin user
- Start both backend and frontend servers
- Display login credentials

### Option 2: Manual Setup

### 1. Clone and Setup

```bash
cd ai-web-app
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Copy environment template and configure
cp backend/.env.template.new backend/.env
# Configure AWS region (credentials handled by AWS CLI)
echo "AWS_DEFAULT_REGION=us-east-1" >> backend/.env
```

### 3. AWS Configuration (SECURE SETUP)

**🔐 New Secure Credential Management**: This application now uses AWS CLI credentials instead of storing them in `.env` files for better security.

#### Option 1: AWS CLI (Recommended)
```bash
# Install AWS CLI
brew install awscli  # macOS
# or follow AWS documentation for other platforms

# Configure credentials securely
aws configure
```

#### Option 2: AWS Profiles (Multiple Environments)
```bash
# Configure different profiles
aws configure --profile development
aws configure --profile production

# Set profile in .env
echo "AWS_PROFILE=development" >> backend/.env
```

#### Additional Setup:
1. Enable Bedrock models in AWS Console
2. Configure IAM permissions (see docs/AWS_SETUP.md)
3. Test setup: `python test_aws_credentials.py`

For detailed instructions, see:
- `docs/SECURE_AWS_CREDENTIALS.md` - New secure credential guide
- `docs/AWS_SETUP.md` - Original AWS setup guide

### 4. Run the Application

```bash
# Start the backend server
cd backend
python app.py

# In a new terminal, serve the frontend
cd frontend
# Using Python's built-in server:
python -m http.server 8000
# Or using any other static file server
```

### 5. Access the Application

Open your browser and navigate to:
- Frontend: `http://localhost:8000`
- Backend API: `http://localhost:5001`

### 6. First Login

Use the default admin credentials:
- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Important**: Change the default password immediately after first login!

For detailed authentication information, see [AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md).

## Project Structure

```
ai-web-app/
├── README.md
├── AUTHENTICATION_GUIDE.md   # Detailed authentication documentation
├── start.sh                  # Linux/Mac startup script
├── start.bat                 # Windows startup script
├── docs/
│   └── AWS_SETUP.md          # Detailed AWS setup instructions
├── backend/
│   ├── app.py                # Main Flask application
│   ├── config.py             # Configuration settings
│   ├── models.py             # Database models (Users, Logs, etc.)
│   ├── auth.py               # Authentication routes and logic
│   ├── logs.py               # Logging routes and utilities
│   ├── init_db.py            # Database initialization script
│   ├── requirements.txt      # Python dependencies
│   ├── .env.template         # Environment variables template
│   ├── ai_web_app.db         # SQLite database (auto-created)
│   └── uploads/              # Temporary file uploads (auto-created)
└── frontend/
    ├── index.html            # Main HTML file with auth modals
    ├── style.css             # Styling and responsive design
    └── script.js             # Frontend JavaScript with auth logic
```

## API Endpoints

### Authentication Endpoints (New)
- **POST** `/api/auth/register` - User registration
- **POST** `/api/auth/login` - User login
- **POST** `/api/auth/logout` - User logout
- **GET** `/api/auth/check` - Check authentication status
- **GET** `/api/auth/profile` - Get user profile
- **PUT** `/api/auth/profile` - Update user profile
- **POST** `/api/auth/change-password` - Change password

### Logging Endpoints (New)
- **GET** `/api/logs/searches` - Get search history
- **GET** `/api/logs/actions` - Get user actions
- **GET** `/api/logs/logins` - Get login history
- **GET** `/api/logs/stats` - Get usage statistics
- **GET** `/api/logs/export` - Export all user data

### AI Endpoints (Now Protected)
- **POST** `/api/chat` - General purpose AI chat
- **POST** `/api/code-chat` - Coding assistant
- **POST** `/api/document-analyze` - Document analysis
- **POST** `/api/generate-image` - Image generation
- **POST** `/api/analyze-image` - Image analysis

### System Endpoints
- **GET** `/api/health` - Health check with auth status

**Note**: All AI endpoints now require authentication. Users must be logged in to access these features.

## Supported File Types

### Documents
- Text files (.txt)
- PDF files (.pdf)
- Word documents (.doc, .docx)

### Images
- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Required
AWS_DEFAULT_REGION=us-east-1
SECRET_KEY=your-flask-secret-key

# Optional - AWS Profile (recommended for multiple environments)
AWS_PROFILE=your-profile-name

# Legacy (NOT RECOMMENDED - use AWS CLI instead)
# AWS_ACCESS_KEY_ID=your_access_key
# AWS_SECRET_ACCESS_KEY=your_secret_key
```

**Security Note**: The application now prioritizes AWS CLI credentials over environment variables. Use `aws configure` for secure credential management.

### Model Configuration

The application uses these AWS Bedrock models by default:
- **Claude 3 Sonnet**: `anthropic.claude-3-sonnet-20240229-v1:0`
- **Titan Image Generator**: `amazon.titan-image-generator-v1`

You can modify these in `config.py` or override via environment variables.

## Features in Detail

### 🤖 AI Chatbot
- General purpose conversational AI
- Supports markdown formatting in responses
- Real-time chat interface
- Message history within session

### 📄 Document Analyzer
- Upload documents via drag-and-drop or file picker
- Extracts key insights and summaries
- Supports multiple document formats
- Automatic file cleanup after processing

### 💻 Coding Assistant
- Specialized for programming questions
- Code syntax highlighting
- Supports multiple programming languages
- Best practices and debugging help

### 🎨 Image Generator
- Text-to-image generation using Titan
- Customizable prompts
- Download generated images
- High-quality 512x512 output

### 🔍 Image Analyzer
- Upload images for AI analysis
- Detailed descriptions of image content
- Object and scene recognition
- Visual preview of uploaded images

## Troubleshooting

### Common Issues

1. **AWS Bedrock Access Denied**
   - Ensure you have requested access to models in AWS Console
   - Check IAM permissions
   - Verify AWS credentials

2. **Backend Connection Failed**
   - Make sure Flask server is running on port 5000
   - Check firewall settings
   - Verify CORS configuration

3. **File Upload Issues**
   - Check file size limits (16MB max)
   - Ensure file types are supported
   - Verify upload directory permissions

### Debug Mode

Enable debug mode by setting `FLASK_ENV=development` in your `.env` file.

## Security Considerations

- Never commit AWS credentials to version control
- Use IAM roles with minimal required permissions
- Implement rate limiting for production use
- Validate and sanitize all file uploads
- Use HTTPS in production

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review AWS Bedrock documentation
3. Open an issue on the repository

## Acknowledgments

- AWS Bedrock for AI model access
- Anthropic Claude for conversational AI
- Amazon Titan for image generation
- Flask community for the web framework
