# AI Web App Database Query Instructions

This document provides comprehensive instructions for querying the `ai_web_app.db` SQLite database.

## Database Location
- **Primary Database**: `ai-web-app/backend/instance/ai_web_app.db`
- **Backup Database**: `ai-web-app/instance/ai_web_app.db` (legacy location)

## Current Admin Credentials
- **Username**: `admin`
- **Password**: `newadmin123`
- **Email**: `admin@example.com`

---

## Method 1: SQLite3 Command Line

### Basic Commands
```bash
# Navigate to backend directory
cd ai-web-app/backend

# Show all tables
sqlite3 instance/ai_web_app.db ".tables"

# Show table schema
sqlite3 instance/ai_web_app.db ".schema users"
sqlite3 instance/ai_web_app.db ".schema login_logs"
sqlite3 instance/ai_web_app.db ".schema user_actions"
sqlite3 instance/ai_web_app.db ".schema signup_codes"

# Enable headers and column mode for better output
sqlite3 instance/ai_web_app.db ".headers on" ".mode column"
```

### Common Queries

#### Users Table
```bash
# List all users
sqlite3 instance/ai_web_app.db "SELECT id, username, email, is_admin, is_active, created_at FROM users;"

# Find admin users
sqlite3 instance/ai_web_app.db "SELECT * FROM users WHERE is_admin = 1;"

# Find active users
sqlite3 instance/ai_web_app.db "SELECT * FROM users WHERE is_active = 1;"

# Count total users
sqlite3 instance/ai_web_app.db "SELECT COUNT(*) as total_users FROM users;"
```

#### Login Logs
```bash
# Recent login attempts
sqlite3 instance/ai_web_app.db "SELECT username_attempted, success, ip_address, login_time, failure_reason FROM login_logs ORDER BY login_time DESC LIMIT 10;"

# Failed login attempts
sqlite3 instance/ai_web_app.db "SELECT * FROM login_logs WHERE success = 0 ORDER BY login_time DESC;"

# Successful logins for specific user
sqlite3 instance/ai_web_app.db "SELECT * FROM login_logs WHERE username_attempted = 'admin' AND success = 1;"
```

#### User Actions
```bash
# Recent user actions
sqlite3 instance/ai_web_app.db "SELECT u.username, ua.action_type, ua.ip_address, ua.timestamp FROM user_actions ua JOIN users u ON ua.user_id = u.id ORDER BY ua.timestamp DESC LIMIT 10;"

# Actions by specific user
sqlite3 instance/ai_web_app.db "SELECT * FROM user_actions WHERE user_id = 3 ORDER BY timestamp DESC;"

# Password change actions
sqlite3 instance/ai_web_app.db "SELECT u.username, ua.timestamp FROM user_actions ua JOIN users u ON ua.user_id = u.id WHERE ua.action_type = 'password_change';"
```

#### Signup Codes
```bash
# List all signup codes
sqlite3 instance/ai_web_app.db "SELECT code, expires_at, used_by_user_id, created_at FROM signup_codes ORDER BY created_at DESC;"

# Unused signup codes
sqlite3 instance/ai_web_app.db "SELECT * FROM signup_codes WHERE used_by_user_id IS NULL;"

# Expired codes
sqlite3 instance/ai_web_app.db "SELECT * FROM signup_codes WHERE expires_at < datetime('now');"
```

---

## Method 2: Python Query Tool

### Setup and Usage
```bash
# Navigate to backend directory
cd ai-web-app/backend

# Run comprehensive database overview
python query_db.py

# Run custom SQL queries
python query_db.py "YOUR_SQL_QUERY_HERE"
```

### Example Custom Queries
```bash
# Find user by username
python query_db.py "SELECT * FROM users WHERE username = 'admin';"

# Get login history for last 24 hours
python query_db.py "SELECT * FROM login_logs WHERE login_time > datetime('now', '-1 day');"

# Count actions by type
python query_db.py "SELECT action_type, COUNT(*) as count FROM user_actions GROUP BY action_type;"

# Find users created in last week
python query_db.py "SELECT * FROM users WHERE created_at > datetime('now', '-7 days');"
```

---

## Method 3: Python Script Integration

### Direct Database Connection
```python
import sqlite3

def query_database():
    conn = sqlite3.connect('ai-web-app/backend/instance/ai_web_app.db')
    cursor = conn.cursor()
    
    # Your queries here
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    
    for row in results:
        print(row)
    
    conn.close()
```

### Using the Models (Flask App Context)
```python
# From within the Flask app context
from models import User, LoginLog, UserAction, SignupCode

# Query users
users = User.query.all()
admin_users = User.query.filter_by(is_admin=True).all()

# Query login logs
recent_logins = LoginLog.query.order_by(LoginLog.login_time.desc()).limit(10).all()

# Query user actions
actions = UserAction.query.order_by(UserAction.timestamp.desc()).limit(10).all()
```

---

## Database Schema Reference

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME,
    last_login DATETIME,
    is_admin BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL
);
```

### Login Logs Table
```sql
CREATE TABLE login_logs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    username_attempted VARCHAR(80) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    user_agent VARCHAR(500),
    login_time DATETIME,
    success BOOLEAN NOT NULL,
    failure_reason VARCHAR(100),
    FOREIGN KEY(user_id) REFERENCES users (id)
);
```

### User Actions Table
```sql
CREATE TABLE user_actions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    details TEXT,
    timestamp DATETIME,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    FOREIGN KEY(user_id) REFERENCES users (id)
);
```

### Signup Codes Table
```sql
CREATE TABLE signup_codes (
    id INTEGER PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    expires_at DATETIME NOT NULL,
    used_by_user_id INTEGER,
    created_at DATETIME,
    FOREIGN KEY(used_by_user_id) REFERENCES users (id)
);
```

---

## Useful Query Examples

### Security Monitoring
```sql
-- Failed login attempts in last hour
SELECT username_attempted, COUNT(*) as attempts, ip_address 
FROM login_logs 
WHERE success = 0 AND login_time > datetime('now', '-1 hour') 
GROUP BY username_attempted, ip_address;

-- Multiple failed attempts from same IP
SELECT ip_address, COUNT(*) as failed_attempts 
FROM login_logs 
WHERE success = 0 
GROUP BY ip_address 
HAVING COUNT(*) > 5;
```

### User Management
```sql
-- Users who haven't logged in recently
SELECT username, email, last_login 
FROM users 
WHERE last_login < datetime('now', '-30 days') OR last_login IS NULL;

-- Most active users
SELECT u.username, COUNT(ua.id) as action_count 
FROM users u 
LEFT JOIN user_actions ua ON u.id = ua.user_id 
GROUP BY u.id 
ORDER BY action_count DESC;
```

### System Statistics
```sql
-- Daily user registrations
SELECT DATE(created_at) as date, COUNT(*) as registrations 
FROM users 
GROUP BY DATE(created_at) 
ORDER BY date DESC;

-- Login success rate
SELECT 
    COUNT(CASE WHEN success = 1 THEN 1 END) as successful_logins,
    COUNT(CASE WHEN success = 0 THEN 1 END) as failed_logins,
    ROUND(COUNT(CASE WHEN success = 1 THEN 1 END) * 100.0 / COUNT(*), 2) as success_rate
FROM login_logs;
```

---

## Troubleshooting

### Common Issues
1. **Database locked**: Make sure Flask app is not running when using sqlite3 command line
2. **Permission denied**: Check file permissions on database file
3. **No such table**: Verify you're using the correct database file path

### Database Backup
```bash
# Create backup
sqlite3 ai-web-app/backend/instance/ai_web_app.db ".backup backup_$(date +%Y%m%d_%H%M%S).db"

# Restore from backup
sqlite3 ai-web-app/backend/instance/ai_web_app.db ".restore backup_file.db"
```

### Reset Database (if needed)
```bash
cd ai-web-app/backend
python init_db.py  # Reinitialize database
python reset_admin.py  # Create fresh admin user
```

---

## Quick Reference Commands

```bash
# Most commonly used commands
cd ai-web-app/backend

# Database overview
python query_db.py

# Check admin user
python query_db.py "SELECT * FROM users WHERE is_admin = 1;"

# Recent activity
python query_db.py "SELECT * FROM login_logs ORDER BY login_time DESC LIMIT 5;"

# User count
python query_db.py "SELECT COUNT(*) FROM users;"

# Available signup codes
python query_db.py "SELECT code FROM signup_codes WHERE used_by_user_id IS NULL;"
```

This instruction file provides all the methods and examples needed to effectively query and manage the AI Web App database.
