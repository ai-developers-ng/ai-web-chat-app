#!/usr/bin/env python3
"""
Database initialization script for AI Web App
"""

import os
import sys
from flask import Flask
from models import db, User
from config import Config

def create_app():
    """Create Flask app for database initialization"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    db.init_app(app)
    
    return app

def init_database():
    """Initialize the database with tables"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Check if admin user exists
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                # Create default admin user
                admin_user = User(
                    username='admin',
                    email='admin@example.com',
                    is_admin=True,
                    is_active=True
                )
                admin_user.set_password('admin123')
                
                db.session.add(admin_user)
                db.session.commit()
                
                print("✅ Default admin user created!")
                print("   Username: admin")
                print("   Password: admin123")
                print("   Email: admin@example.com")
                print("   Admin: Yes")
                print("   ⚠️  Please change the default password after first login!")
            else:
                # Ensure existing admin user has admin privileges
                if not admin_user.is_admin:
                    admin_user.is_admin = True
                    db.session.commit()
                    print("✅ Admin privileges granted to existing admin user")
                print("ℹ️  Admin user already exists")
            
            # Print database info
            print(f"\n📊 Database Information:")
            print(f"   Database URI: {Config.SQLALCHEMY_DATABASE_URI}")
            print(f"   Total users: {User.query.count()}")
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            sys.exit(1)

if __name__ == '__main__':
    print("🚀 Initializing AI Web App Database...")
    init_database()
    print("✅ Database initialization complete!")
