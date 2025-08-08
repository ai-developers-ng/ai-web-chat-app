# Authentication and Logging Guide

This guide explains the authentication system and comprehensive logging features added to the AI Web Application.

## 🔐 Authentication System

### Features
- **User Registration**: Create new accounts with username, email, and password
- **User Login**: Secure login with username/email and password
- **Session Management**: Persistent login sessions with Flask-Login
- **Password Security**: Passwords are hashed using Werkzeug's security functions
- **Input Validation**: Email format validation and password strength requirements

### Password Requirements
- Minimum 8 characters
- Must contain at least one letter
- Must contain at least one number

### Default Admin Account
When you first run the application, a default admin account is created:
- **Username**: `admin`
- **Email**: `admin@example.com`
- **Password**: `admin123`

⚠️ **Important**: Change the default password immediately after first login!

## 📊 Comprehensive Logging System

### What Gets Logged

#### 1. Search Logs
All AI interactions are logged with:
- Search type (chat, code, document, image_gen, image_analyze)
- User query/prompt
- AI response
- Response time
- Timestamp
- User IP address and browser info

#### 2. User Actions
All user activities are tracked:
- Login/logout events
- File uploads (with file details)
- Tab switches
- Profile updates
- Password changes
- Data exports

#### 3. Login Logs
All login attempts are recorded:
- Username attempted
- Success/failure status
- Failure reason (if applicable)
- IP address and browser info
- Timestamp

### Database Tables

#### Users Table
```sql
- id: Primary key
- username: Unique username
- email: Unique email address
- password_hash: Hashed password
- created_at: Account creation timestamp
- last_login: Last successful login
- is_active: Account status
```

#### Search Logs Table
```sql
- id: Primary key
- user_id: Foreign key to users
- search_type: Type of search/query
- query: User's input
- response: AI's response
- response_time: Time taken to respond
- timestamp: When the search occurred
- ip_address: User's IP address
- user_agent: Browser information
```

#### User Actions Table
```sql
- id: Primary key
- user_id: Foreign key to users
- action_type: Type of action performed
- details: JSON with additional details
- timestamp: When the action occurred
- ip_address: User's IP address
- user_agent: Browser information
```

#### Login Logs Table
```sql
- id: Primary key
- user_id: Foreign key to users (null for failed attempts)
- username_attempted: Username that was tried
- ip_address: User's IP address
- user_agent: Browser information
- login_time: When the attempt occurred
- success: Whether login was successful
- failure_reason: Reason for failure (if applicable)
```

## 🚀 Getting Started

### 1. Installation
Run the startup script which will automatically initialize the database:

**Linux/Mac:**
```bash
./start.sh
```

**Windows:**
```batch
start.bat
```

### 2. First Login
1. Open http://localhost:8000 in your browser
2. Click "Login" in the top-right corner
3. Use the default admin credentials:
   - Username: `admin`
   - Password: `admin123`
4. **Important**: Change the password immediately!

### 3. Creating New Users
1. Click "Register" to create a new account
2. Fill in username, email, and password
3. Password must meet the requirements listed above
4. After registration, login with your new credentials

## 📱 Using the Application

### Protected Features
All AI features require authentication:
- AI Chatbot
- Document Analyzer
- Coding Assistant
- Image Generator
- Image Analyzer

### Activity History
Once logged in, you can access your activity history:
1. Click the "History" button in the header
2. View different types of logs:
   - **Searches**: All your AI interactions
   - **Actions**: Your activity on the platform
   - **Logins**: Your login history
   - **Statistics**: Summary of your usage

### Profile Management
- Click your username in the header to access profile
- View account information
- Export all your data as JSON
- Change password (coming soon)

## 🔒 Security Features

### Password Security
- Passwords are hashed using Werkzeug's PBKDF2 with salt
- No plain text passwords are stored
- Session cookies are secure and HTTP-only

### Input Validation
- Email format validation
- Username length requirements (minimum 3 characters)
- Password strength validation
- SQL injection protection through SQLAlchemy ORM

### Session Management
- Secure session handling with Flask-Login
- Automatic logout on browser close
- Session timeout protection

## 📊 Data Export

Users can export all their data:
1. Go to Profile (click username in header)
2. Click "Export Data"
3. Downloads a JSON file containing:
   - User profile information
   - All search history
   - All user actions
   - All login logs

## 🛠️ API Endpoints

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/check` - Check authentication status
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile
- `POST /api/auth/change-password` - Change password

### Logging Endpoints
- `GET /api/logs/searches` - Get search history
- `GET /api/logs/actions` - Get user actions
- `GET /api/logs/logins` - Get login history
- `GET /api/logs/stats` - Get usage statistics
- `GET /api/logs/export` - Export all user data

### Protected AI Endpoints
All existing AI endpoints now require authentication:
- `POST /api/chat` - AI chatbot
- `POST /api/code-chat` - Coding assistant
- `POST /api/document-analyze` - Document analyzer
- `POST /api/generate-image` - Image generator
- `POST /api/analyze-image` - Image analyzer

## 🔧 Configuration

### Database Configuration
The application uses SQLite by default. The database file `ai_web_app.db` is created automatically in the backend directory.

To use a different database, update the `SQLALCHEMY_DATABASE_URI` in `backend/config.py`:

```python
# For PostgreSQL
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/ai_web_app'

# For MySQL
SQLALCHEMY_DATABASE_URI = 'mysql://user:password@localhost/ai_web_app'
```

### CORS Configuration
The application is configured to accept requests from:
- http://localhost:3000
- http://127.0.0.1:3000
- http://localhost:5000
- http://127.0.0.1:5000

Update the CORS origins in `backend/app.py` if needed.

## 🐛 Troubleshooting

### Common Issues

#### "Database not found" Error
Run the database initialization script:
```bash
cd backend
python init_db.py
```

#### "Authentication required" Error
Make sure you're logged in. The application will redirect you to login if your session expires.

#### "CORS Error" in Browser
Check that the frontend is running on the correct port and that CORS is configured properly in the backend.

### Logs and Debugging
- Backend logs are displayed in the terminal where you started the server
- Check the browser's developer console for frontend errors
- Database errors are logged to the backend console

## 📈 Usage Statistics

The application tracks comprehensive usage statistics:
- Total searches by type
- Total user actions by type
- Login success/failure rates
- Response times for AI queries
- User activity patterns

Access statistics through the History tab → Statistics section.

## 🔄 Data Migration

If you need to migrate data or reset the database:

1. **Backup existing data**:
   ```bash
   cp backend/ai_web_app.db backend/ai_web_app.db.backup
   ```

2. **Reset database**:
   ```bash
   rm backend/ai_web_app.db
   cd backend
   python init_db.py
   ```

3. **Restore from backup** (if needed):
   ```bash
   cp backend/ai_web_app.db.backup backend/ai_web_app.db
   ```

## 🤝 Contributing

When contributing to the authentication system:
1. Follow the existing code patterns
2. Add appropriate logging for new features
3. Update this documentation
4. Test authentication flows thoroughly
5. Ensure proper input validation

## 📞 Support

For issues related to authentication or logging:
1. Check this guide first
2. Review the application logs
3. Check the browser developer console
4. Ensure all dependencies are installed correctly

The authentication system is designed to be secure, user-friendly, and comprehensive in its logging capabilities while maintaining the existing functionality of the AI Web Application.
