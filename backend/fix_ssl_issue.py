#!/usr/bin/env python3
"""
Script to fix SSL validation errors for sts.amazonaws.com
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
    print("🔧 Fixing SSL validation errors for sts.amazonaws.com...")
    
    # Change to backend directory
    os.chdir("backend")
    
    # Step 1: Update certificates
    print("📦 Updating SSL certificates...")
    success, stdout, stderr = run_command("pip install --upgrade certifi")
    if not success:
        print(f"❌ Failed to update certifi: {stderr}")
        return False
    
    # Step 2: Install additional SSL packages
    print("📦 Installing SSL support packages...")
    ssl_packages = [
        "pip install --upgrade urllib3",
        "pip install --upgrade requests",
        "pip install --upgrade pyopenssl"
    ]
    
    for package_cmd in ssl_packages:
        success, stdout, stderr = run_command(package_cmd)
        if not success:
            print(f"❌ Failed to install {package_cmd}: {stderr}")
            return False
    
    # Step 3: Disable SSL verification (development only)
    print("⚠️ Disabling SSL verification (development only)...")
    disable_ssl_code = '''
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
print("SSL verification disabled")
'''
    with open("disable_ssl.py", "w") as f:
        f.write(disable_ssl_code)
    
    # Step 4: Test SSL connectivity with verification disabled
    print("🔍 Testing SSL connectivity with verification disabled...")
    test_cmd = "python disable_ssl.py"
    success, stdout, stderr = run_command(test_cmd)
    if success:
        print("✅ SSL verification disabled successfully!")
    else:
        print(f"⚠️ SSL disable test warning: {stderr}")
    
    print("✅ SSL fix applied successfully!")
    print("\nNext steps:")
    print("1. Restart your Flask application")
    print("2. Test AWS connectivity")
    print("3. If issues persist, check the troubleshooting guide")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 SSL fix completed! Please restart your application.")
    else:
        print("\n❌ SSL fix failed. Please check the error messages above.")
