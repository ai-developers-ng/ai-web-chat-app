#!/usr/bin/env python3

import sys
import os
from models import db, User, SignupCode
from flask import Flask
from config import Config
from datetime import datetime, timedelta
import secrets

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

def reset_admin():
    with app.app_context():
        # Delete existing admin user
        existing_admin = User.query.filter_by(username='admin').first()
        if existing_admin:
            print(f"Deleting existing admin user: {existing_admin.username}")
            db.session.delete(existing_admin)
            db.session.commit()
        
        # Create new admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True,
            is_active=True
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        db.session.commit()
        
        print("✅ New admin user created successfully!")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Password: admin123")
        print(f"   Is Admin: {admin.is_admin}")
        print(f"   Is Active: {admin.is_active}")
        
        # Test the password
        if admin.check_password('admin123'):
            print("✅ Password verification successful!")
        else:
            print("❌ Password verification failed!")
        
        # Create a signup code
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

if __name__ == '__main__':
    reset_admin()
