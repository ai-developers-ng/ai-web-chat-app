#!/usr/bin/env python3
"""
Script to create an admin user and generate a signup code for testing
"""

import os
import sys
from datetime import datetime, timedelta
import secrets

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import Flask app and models
from flask import Flask
from config import Config
from models import db, User, SignupCode

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

def create_admin_user():
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Check if admin user already exists
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            print(f"Admin user already exists: {admin_user.username}")
            admin_user.is_admin = True
            db.session.commit()
        else:
            # Create admin user
            admin_user = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print(f"Created admin user: {admin_user.username}")
        
        # Generate a signup code
        code = secrets.token_hex(16)
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        signup_code = SignupCode(
            code=code,
            expires_at=expires_at
        )
        
        db.session.add(signup_code)
        db.session.commit()
        
        print(f"Generated signup code: {code}")
        print(f"Expires at: {expires_at}")
        print(f"Admin login: username='admin', password='admin123'")

if __name__ == '__main__':
    create_admin_user()
