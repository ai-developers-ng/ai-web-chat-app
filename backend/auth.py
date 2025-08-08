from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, LoginLog, UserAction, SignupCode
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__)

def get_client_info():
    """Get client IP and user agent"""
    ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
    user_agent = request.headers.get('User-Agent', 'unknown')
    return ip_address, user_agent

def log_user_action(action_type, details=None):
    """Log user action"""
    if current_user.is_authenticated:
        ip_address, user_agent = get_client_info()
        action = UserAction(
            user_id=current_user.id,
            action_type=action_type,
            ip_address=ip_address,
            user_agent=user_agent
        )
        if details:
            action.set_details(details)
        db.session.add(action)
        db.session.commit()

def log_login_attempt(username, success, user_id=None, failure_reason=None):
    """Log login attempt"""
    ip_address, user_agent = get_client_info()
    login_log = LoginLog(
        user_id=user_id,
        username_attempted=username,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        failure_reason=failure_reason
    )
    db.session.add(login_log)
    db.session.commit()

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        signup_code_str = data.get('signup_code', '').strip()
        
        # Validation
        if not username or not email or not password or not signup_code_str:
            return jsonify({'error': 'Username, email, password, and signup code are required'}), 400
        
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters long'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        is_valid, password_message = validate_password(password)
        if not is_valid:
            return jsonify({'error': password_message}), 400
        
        # Validate signup code
        signup_code = SignupCode.query.filter_by(code=signup_code_str).first()
        if not signup_code or not signup_code.is_valid():
            return jsonify({'error': 'Invalid or expired signup code'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()  # Commit to get user ID
        
        # Mark signup code as used
        signup_code.used_by_user_id = user.id
        db.session.add(signup_code)
        
        # Log registration action
        ip_address, user_agent = get_client_info()
        action = UserAction(
            user_id=user.id,
            action_type='register',
            ip_address=ip_address,
            user_agent=user_agent
        )
        action.set_details({'email': email})
        db.session.add(action)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            log_login_attempt(username, False, failure_reason='invalid_username')
            return jsonify({'error': 'Invalid username or password'}), 401
        
        if not user.check_password(password):
            log_login_attempt(username, False, user.id, 'invalid_password')
            return jsonify({'error': 'Invalid username or password'}), 401
        
        if not user.is_active:
            log_login_attempt(username, False, user.id, 'account_disabled')
            return jsonify({'error': 'Account is disabled'}), 401
        
        # Login successful
        login_user(user, remember=True)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Log successful login
        log_login_attempt(username, True, user.id)
        log_user_action('login')
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """User logout endpoint"""
    try:
        log_user_action('logout')
        logout_user()
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        return jsonify({'error': f'Logout failed: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Get current user profile"""
    try:
        return jsonify({
            'user': current_user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        
        if email and email != current_user.email:
            if not validate_email(email):
                return jsonify({'error': 'Invalid email format'}), 400
            
            # Check if email is already taken
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != current_user.id:
                return jsonify({'error': 'Email already registered'}), 400
            
            current_user.email = email
        
        db.session.commit()
        
        log_user_action('profile_update', {'updated_fields': ['email'] if email else []})
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Profile update failed: {str(e)}'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        if not current_user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        is_valid, password_message = validate_password(new_password)
        if not is_valid:
            return jsonify({'error': password_message}), 400
        
        current_user.set_password(new_password)
        db.session.commit()
        
        log_user_action('password_change')
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Password change failed: {str(e)}'}), 500

@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': current_user.to_dict()
        }), 200
    else:
        return jsonify({'authenticated': False}), 200
