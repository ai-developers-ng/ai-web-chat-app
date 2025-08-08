#!/usr/bin/env python3
"""
Test script to verify the AI Web Application setup
"""

import sys
import os
import subprocess
import importlib.util

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.8+")
        return False

def check_required_packages():
    """Check if required packages can be imported"""
    print("\n📦 Checking required packages...")
    
    required_packages = [
        'flask',
        'flask_cors',
        'boto3',
        'dotenv',
        'PIL',
        'werkzeug'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'dotenv':
                importlib.import_module('dotenv')
            elif package == 'PIL':
                importlib.import_module('PIL')
            elif package == 'flask_cors':
                importlib.import_module('flask_cors')
            else:
                importlib.import_module(package)
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    return len(missing_packages) == 0, missing_packages

def check_aws_cli():
    """Check if AWS CLI is installed"""
    print("\n☁️  Checking AWS CLI...")
    try:
        result = subprocess.run(['aws', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ AWS CLI - {result.stdout.strip()}")
            return True
        else:
            print("❌ AWS CLI - Not working properly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ AWS CLI - Not installed")
        return False

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    print("\n🔑 Checking AWS credentials...")
    try:
        result = subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ AWS credentials - Configured")
            return True
        else:
            print("❌ AWS credentials - Not configured or invalid")
            print("Run 'aws configure' to set up your credentials")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ AWS credentials - Cannot check (AWS CLI not available)")
        return False

def check_bedrock_access():
    """Check if AWS Bedrock is accessible"""
    print("\n🤖 Checking AWS Bedrock access...")
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
        
        client = boto3.client('bedrock', region_name='us-east-1')
        response = client.list_foundation_models()
        
        claude_models = [model for model in response['modelSummaries'] 
                        if 'claude' in model['modelId'].lower()]
        titan_models = [model for model in response['modelSummaries'] 
                       if 'titan' in model['modelId'].lower()]
        
        print(f"✅ Bedrock access - OK ({len(response['modelSummaries'])} models available)")
        print(f"   Claude models: {len(claude_models)}")
        print(f"   Titan models: {len(titan_models)}")
        
        return True
        
    except NoCredentialsError:
        print("❌ Bedrock access - No AWS credentials")
        return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'UnauthorizedOperation':
            print("❌ Bedrock access - Permission denied")
            print("   Make sure you have bedrock:ListFoundationModels permission")
        else:
            print(f"❌ Bedrock access - Error: {error_code}")
        return False
    except Exception as e:
        print(f"❌ Bedrock access - Error: {str(e)}")
        return False

def check_file_structure():
    """Check if all required files exist"""
    print("\n📁 Checking file structure...")
    
    required_files = [
        'README.md',
        'backend/app.py',
        'backend/config.py',
        'backend/requirements.txt',
        'backend/.env.template',
        'frontend/index.html',
        'frontend/style.css',
        'frontend/script.js',
        'docs/AWS_SETUP.md'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
            missing_files.append(file_path)
    
    return len(missing_files) == 0, missing_files

def main():
    """Run all checks"""
    print("🔍 AI Web Application Setup Test")
    print("=" * 40)
    
    checks = []
    
    # Run all checks
    checks.append(("Python Version", check_python_version()))
    checks.append(("File Structure", check_file_structure()))
    checks.append(("Required Packages", check_required_packages()))
    checks.append(("AWS CLI", check_aws_cli()))
    checks.append(("AWS Credentials", check_aws_credentials()))
    checks.append(("Bedrock Access", check_bedrock_access()))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 SUMMARY")
    print("=" * 40)
    
    passed = 0
    total = len(checks)
    
    for check_name, result in checks:
        if isinstance(result, tuple):
            result = result[0]  # Extract boolean from tuple
        
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nResult: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Your setup is ready.")
        print("Run './start.sh' (Linux/Mac) or 'start.bat' (Windows) to start the application.")
    else:
        print(f"\n⚠️  {total - passed} checks failed. Please fix the issues above.")
        print("Refer to README.md and docs/AWS_SETUP.md for setup instructions.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
