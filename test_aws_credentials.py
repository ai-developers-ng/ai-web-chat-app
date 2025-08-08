#!/usr/bin/env python3
"""
AWS Credentials Test Script

This script tests the new secure AWS credential management system.
Run this script to verify your AWS credentials are properly configured.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from aws_credentials import get_credential_manager
from botocore.exceptions import NoCredentialsError
import json

def test_credentials():
    """Test AWS credentials and Bedrock access."""
    print("🔐 Testing AWS Credentials...")
    print("=" * 50)
    
    try:
        # Initialize credential manager
        manager = get_credential_manager()
        
        # Get credential information
        print("📋 Credential Information:")
        cred_info = manager.get_credentials_info()
        
        for key, value in cred_info.items():
            if key == 'account_id' and value:
                # Mask account ID for security
                masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:]
                print(f"   {key}: {masked_value}")
            else:
                print(f"   {key}: {value}")
        
        print("\n🧪 Testing Bedrock Access...")
        bedrock_test = manager.test_bedrock_access()
        
        if bedrock_test['success']:
            print("✅ Bedrock Access: SUCCESS")
            print(f"   Models Available: {bedrock_test['models_available']}")
            print(f"   Region: {bedrock_test['region']}")
            print(f"   Credentials Source: {bedrock_test['credentials_source']}")
        else:
            print("❌ Bedrock Access: FAILED")
            print(f"   Error: {bedrock_test.get('error_message', bedrock_test.get('error', 'Unknown error'))}")
            print(f"   Error Code: {bedrock_test.get('error_code', 'N/A')}")
            
            # Provide troubleshooting suggestions
            print("\n🔧 Troubleshooting Suggestions:")
            error_code = bedrock_test.get('error_code', '')
            
            if error_code == 'AccessDeniedException':
                print("   - Check IAM permissions for Bedrock access")
                print("   - Ensure you have requested access to Bedrock models in AWS Console")
                print("   - Verify your AWS account has Bedrock enabled")
            elif error_code == 'UnauthorizedOperation':
                print("   - Check your AWS credentials have the necessary permissions")
                print("   - Verify the IAM policy includes Bedrock actions")
            else:
                print("   - Verify AWS credentials are valid: aws sts get-caller-identity")
                print("   - Check AWS region supports Bedrock")
                print("   - Ensure Bedrock models are enabled in AWS Console")
        
        print("\n📊 Summary:")
        print(f"   ✅ Credentials Found: {cred_info.get('source', 'Unknown')}")
        print(f"   ✅ Region: {cred_info.get('region', 'Unknown')}")
        print(f"   {'✅' if bedrock_test['success'] else '❌'} Bedrock Access: {'Working' if bedrock_test['success'] else 'Failed'}")
        
        return bedrock_test['success']
        
    except NoCredentialsError as e:
        print("❌ No AWS credentials found!")
        print(f"   Error: {e}")
        print("\n🔧 Setup Instructions:")
        print("   1. Install AWS CLI: https://aws.amazon.com/cli/")
        print("   2. Configure credentials: aws configure")
        print("   3. Or set environment variables in .env file")
        print("   4. See docs/SECURE_AWS_CREDENTIALS.md for detailed instructions")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 AI Web App - AWS Credentials Test")
    print("This script tests your AWS credential configuration.\n")
    
    success = test_credentials()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Your AWS credentials are properly configured.")
        print("   You can now run the AI Web App with secure credential management.")
    else:
        print("⚠️  Some tests failed. Please check the errors above and:")
        print("   1. Review the troubleshooting suggestions")
        print("   2. Check docs/SECURE_AWS_CREDENTIALS.md for detailed setup")
        print("   3. Verify your AWS account has Bedrock access")
    
    print("\n📚 For more help, see:")
    print("   - docs/SECURE_AWS_CREDENTIALS.md")
    print("   - docs/AWS_SETUP.md")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
