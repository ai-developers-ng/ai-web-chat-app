from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    search_logs = db.relationship('SearchLog', backref='user', lazy=True, cascade='all, delete-orphan')
    user_actions = db.relationship('UserAction', backref='user', lazy=True, cascade='all, delete-orphan')
    login_logs = db.relationship('LoginLog', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
            'is_admin': self.is_admin
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class SignupCode(db.Model):
    """Model for signup codes"""
    __tablename__ = 'signup_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    user = db.relationship('User', backref=db.backref('signup_code_used', uselist=False))
    
    def is_valid(self):
        """Check if the code is valid (not used and not expired)"""
        return self.used_by_user_id is None and self.expires_at > datetime.utcnow()
    
    def to_dict(self):
        """Convert signup code to dictionary"""
        return {
            'id': self.id,
            'code': self.code,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_used': self.used_by_user_id is not None,
            'used_by_user_id': self.used_by_user_id
        }
    
    def __repr__(self):
        return f'<SignupCode {self.code}>'


class SearchLog(db.Model):
    """Model to log all search/query activities"""
    __tablename__ = 'search_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    search_type = db.Column(db.String(50), nullable=False)  # 'chat', 'code', 'document', 'image_gen', 'image_analyze'
    query = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    response_time = db.Column(db.Float)  # Response time in seconds
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    
    def to_dict(self):
        """Convert search log to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'search_type': self.search_type,
            'query': self.query,
            'response': self.response,
            'response_time': self.response_time,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }
    
    def __repr__(self):
        return f'<SearchLog {self.search_type} by User {self.user_id}>'

class UserAction(db.Model):
    """Model to log all user actions and interactions"""
    __tablename__ = 'user_actions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # 'login', 'logout', 'file_upload', 'tab_switch', etc.
    details = db.Column(db.Text)  # JSON string with additional details
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    
    def set_details(self, details_dict):
        """Set details as JSON string"""
        self.details = json.dumps(details_dict) if details_dict else None
    
    def get_details(self):
        """Get details as dictionary"""
        return json.loads(self.details) if self.details else {}
    
    def to_dict(self):
        """Convert user action to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action_type': self.action_type,
            'details': self.get_details(),
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }
    
    def __repr__(self):
        return f'<UserAction {self.action_type} by User {self.user_id}>'

class LoginLog(db.Model):
    """Model to log all login attempts"""
    __tablename__ = 'login_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Nullable for failed attempts
    username_attempted = db.Column(db.String(80), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.String(500))
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Boolean, nullable=False)
    failure_reason = db.Column(db.String(100))  # 'invalid_username', 'invalid_password', etc.
    
    def to_dict(self):
        """Convert login log to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username_attempted': self.username_attempted,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'login_time': self.login_time.isoformat() if self.login_time else None,
            'success': self.success,
            'failure_reason': self.failure_reason
        }
    
    def __repr__(self):
        return f'<LoginLog {self.username_attempted} - {"Success" if self.success else "Failed"}>'
