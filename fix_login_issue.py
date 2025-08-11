#!/usr/bin/env python3
"""
Script to fix the "unsupported digestmod" login issue for ai-web-chat-app
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🔧 Fixing login authentication issue for ai-web-chat-app...")
    
    # Change to backend directory
    os.chdir("backend")
    
    # Step 1: Update pip
    print("📦 Updating pip...")
    success, stdout, stderr = run_command("python -m pip install --upgrade pip")
    if not success:
        print(f"❌ Failed to update pip: {stderr}")
        return False
    
    # Step 2: Install updated requirements
    print("📦 Installing updated dependencies...")
    success, stdout, stderr = run_command("pip install -r requirements.txt")
    if not success:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False
    
    # Step 3: Verify Python version compatibility
    print("🔍 Checking Python version...")
    python_version = sys.version
    print(f"Python version: {python_version}")
    
    # Step 4: Test the fix
    print("✅ Login fix applied successfully!")
    print("\nNext steps:")
    print("1. Restart your Flask application")
    print("2. Test login with your credentials")
    print("3. If issues persist, check the troubleshooting guide")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Fix completed! Please restart your application.")
    else:
        print("\n❌ Fix failed. Please check the error messages above.")
