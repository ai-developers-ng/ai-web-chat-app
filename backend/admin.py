from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, SignupCode, User
from datetime import datetime, timedelta
import secrets

admin_bp = Blueprint('admin', __name__)

def is_admin():
    """Check if the current user is an admin"""
    return current_user.is_authenticated and current_user.is_admin

@admin_bp.before_request
@login_required
def before_request():
    """Protect all admin routes"""
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403

@admin_bp.route('/signup-codes', methods=['POST'])
def create_signup_code():
    """Create a new signup code"""
    try:
        data = request.get_json()
        expires_in_days = data.get('expires_in_days', 7)
        
        code = secrets.token_hex(16)
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        signup_code = SignupCode(
            code=code,
            expires_at=expires_at
        )
        
        db.session.add(signup_code)
        db.session.commit()
        
        return jsonify({
            'message': 'Signup code created successfully',
            'code': signup_code.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create signup code: {str(e)}'}), 500

@admin_bp.route('/signup-codes', methods=['GET'])
def get_signup_codes():
    """Get all signup codes"""
    try:
        codes = SignupCode.query.order_by(SignupCode.created_at.desc()).all()
        return jsonify({
            'codes': [code.to_dict() for code in codes]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get signup codes: {str(e)}'}), 500

# User Management Endpoints

@admin_bp.route('/users', methods=['GET'])
def get_users():
    """Get all users"""
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get users: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user details"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Store original values for rollback if needed
        original_username = user.username
        original_email = user.email
        original_is_active = user.is_active
        original_is_admin = user.is_admin
        
        # Update username
        if 'username' in data:
            new_username = data['username'].strip()
            if not new_username:
                return jsonify({'error': 'Username cannot be empty'}), 400
            
            if len(new_username) < 3:
                return jsonify({'error': 'Username must be at least 3 characters long'}), 400
            
            # Check if username already exists
            if new_username != original_username:
                existing_user = User.query.filter_by(username=new_username).first()
                if existing_user and existing_user.id != user_id:
                    return jsonify({'error': 'Username already exists'}), 400
                
                user.username = new_username
        
        # Update email
        if 'email' in data:
            new_email = data['email'].strip().lower()
            if not new_email:
                return jsonify({'error': 'Email cannot be empty'}), 400
            
            # Basic email validation
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, new_email):
                return jsonify({'error': 'Invalid email format'}), 400
            
            # Check if email already exists
            if new_email != original_email:
                existing_user = User.query.filter_by(email=new_email).first()
                if existing_user and existing_user.id != user_id:
                    return jsonify({'error': 'Email already exists'}), 400
                
                user.email = new_email
        
        # Update active status
        if 'is_active' in data:
            new_is_active = bool(data['is_active'])
            # Prevent deactivating current user
            if user_id == current_user.id and not new_is_active:
                return jsonify({'error': 'Cannot deactivate your own account'}), 400
            user.is_active = new_is_active
        
        # Update admin status (but prevent removing admin from current user)
        if 'is_admin' in data:
            new_is_admin = bool(data['is_admin'])
            if user_id == current_user.id and not new_is_admin:
                return jsonify({'error': 'Cannot remove admin privileges from your own account'}), 400
            user.is_admin = new_is_admin
        
        # Commit changes
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update user: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
def reset_user_password(user_id):
    """Reset user password"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        new_password = data.get('new_password') if data else None
        
        if not new_password:
            # Generate random password if none provided
            new_password = secrets.token_urlsafe(12)
        
        # Validate password strength
        if len(new_password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({
            'message': 'Password reset successfully',
            'new_password': new_password,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to reset password: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>/block', methods=['POST'])
def block_user(user_id):
    """Block/unblock user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent blocking current admin user
        if user_id == current_user.id:
            return jsonify({'error': 'Cannot block yourself'}), 400
        
        data = request.get_json()
        block_status = data.get('block', True) if data else True
        
        user.is_active = not block_status
        db.session.commit()
        
        action = 'blocked' if block_status else 'unblocked'
        return jsonify({
            'message': f'User {action} successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update user status: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent deleting current admin user
        if user_id == current_user.id:
            return jsonify({'error': 'Cannot delete yourself'}), 400
        
        username = user.username
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'message': f'User "{username}" deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete user: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>/make-admin', methods=['POST'])
def make_admin(user_id):
    """Make user an admin"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.is_admin = True
        db.session.commit()
        
        return jsonify({
            'message': f'User "{user.username}" is now an admin',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to make user admin: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>/remove-admin', methods=['POST'])
def remove_admin(user_id):
    """Remove admin privileges from user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent removing admin from current user
        if user_id == current_user.id:
            return jsonify({'error': 'Cannot remove admin privileges from yourself'}), 400
        
        user.is_admin = False
        db.session.commit()
        
        return jsonify({
            'message': f'Admin privileges removed from user "{user.username}"',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to remove admin privileges: {str(e)}'}), 500
