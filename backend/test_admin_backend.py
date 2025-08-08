#!/usr/bin/env python3

import sys
import os
from models import db, User
from flask import Flask
from config import Config

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

def test_admin_user():
    with app.app_context():
        # Find admin user
        admin = User.query.filter_by(username='shohagh121').first()
        
        if not admin:
            print("❌ Admin user not found!")
            return False
            
        print(f"✅ Admin user found:")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Is Admin: {admin.is_admin}")
        print(f"   Is Active: {admin.is_active}")
        print(f"   Password Hash: {admin.password_hash[:50]}...")
        
        # Test password
        test_passwords = ['Shohagh121@@', 'newadmin123', 'CEkIr2AIg9QsGV0z']
        
        for password in test_passwords:
            if admin.check_password(password):
                print(f"✅ Password '{password}' is CORRECT!")
                return True
            else:
                print(f"❌ Password '{password}' is incorrect")
        
        return False

if __name__ == '__main__':
    test_admin_user()
