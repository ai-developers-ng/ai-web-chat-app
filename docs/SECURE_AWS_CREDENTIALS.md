# Secure AWS Credentials Management Guide

## Overview

This application now uses a secure, multi-layered approach to AWS credential management that prioritizes system-level credentials over environment variables. This significantly improves security by avoiding plain-text credentials in project files.

## Security Improvements

### ✅ What's Better Now:
- **AWS CLI Integration**: Automatically uses `aws configure` credentials
- **Multiple Credential Sources**: Supports AWS profiles, IAM roles, and environment variables
- **Credential Chain Priority**: Follows AWS best practices for credential resolution
- **No Plain Text Storage**: Credentials are managed by AWS CLI, not stored in project files
- **Profile Support**: Can use different AWS profiles for different environments
- **Automatic Detection**: Detects and reports which credential source is being used

### ❌ Previous Security Issues (Now Fixed):
- Plain text credentials in `.env` files
- Risk of accidental commit to version control
- No credential rotation support
- Single credential source

## Credential Priority Order

The application now searches for credentials in this secure order:

1. **AWS CLI Profiles** (`~/.aws/credentials`, `~/.aws/config`)
2. **IAM Roles** (for EC2/ECS deployments)
3. **Environment Variables** (fallback only)

## Setup Instructions

### Option 1: AWS CLI (Recommended)

This is the most secure approach:

```bash
# Install AWS CLI if not already installed
# macOS: brew install awscli
# Linux: See AWS documentation
# Windows: Download from AWS website

# Configure default credentials
aws configure

# Or configure a specific profile
aws configure --profile myproject
```

You'll be prompted for:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., us-east-1)
- Default output format (json)

### Option 2: AWS Profiles

For multiple environments or accounts:

```bash
# Configure different profiles
aws configure --profile development
aws configure --profile production

# Set the profile in your .env file
echo "AWS_PROFILE=development" >> .env
```

### Option 3: IAM Roles (Production)

For production deployments on EC2/ECS:

1. Create an IAM role with Bedrock permissions
2. Attach the role to your EC2 instance or ECS task
3. No additional configuration needed - automatically detected

### Option 4: Environment Variables (Fallback)

Only use this if AWS CLI is not available:

```bash
# In your .env file (NOT RECOMMENDED for production)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1
```

## Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Required
AWS_DEFAULT_REGION=us-east-1

# Optional - specify AWS profile
AWS_PROFILE=your-profile-name

# Legacy fallback (not recommended)
# AWS_ACCESS_KEY_ID=your-access-key
# AWS_SECRET_ACCESS_KEY=your-secret-key
```

### Verification

Check which credentials are being used:

```bash
# Start the application and check logs
python app.py

# Or use the health check endpoint
curl http://localhost:5001/api/health

# Or use the detailed AWS status endpoint (requires login)
curl http://localhost:5001/api/aws-status
```

## API Endpoints

### Health Check
```
GET /api/health
```
Returns basic AWS credential information (public endpoint).

### AWS Status
```
GET /api/aws-status
```
Returns detailed AWS credential and Bedrock access information (requires authentication).

## Troubleshooting

### Common Issues

1. **"No valid AWS credentials found"**
   ```bash
   # Solution: Configure AWS CLI
   aws configure
   
   # Or check existing configuration
   aws configure list
   ```

2. **"Profile not found"**
   ```bash
   # List available profiles
   aws configure list-profiles
   
   # Create the profile
   aws configure --profile your-profile-name
   ```

3. **"Access Denied" for Bedrock**
   ```bash
   # Check your permissions
   aws sts get-caller-identity
   
   # Test Bedrock access
   aws bedrock list-foundation-models --region us-east-1
   ```

4. **"Invalid credentials"**
   ```bash
   # Verify credentials work
   aws sts get-caller-identity
   
   # Reconfigure if needed
   aws configure
   ```

### Debug Information

The application logs will show:
- Which credential source is being used
- AWS region and account information
- Any credential-related errors

Example log output:
```
INFO - AWS Bedrock client initialized successfully using: AWS Profile: development
INFO - AWS Region: us-east-1
INFO - AWS Account: 123456789012
```

## Security Best Practices

### ✅ Do:
- Use `aws configure` for local development
- Use IAM roles for production deployments
- Use different profiles for different environments
- Regularly rotate access keys
- Use least-privilege IAM policies
- Monitor AWS CloudTrail for credential usage

### ❌ Don't:
- Store credentials in `.env` files (use only as fallback)
- Commit credentials to version control
- Use root account credentials
- Share credentials between team members
- Use long-term access keys in production

## IAM Permissions

Your AWS credentials need these permissions for Bedrock:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:ListFoundationModels",
                "bedrock:GetFoundationModel"
            ],
            "Resource": "*"
        }
    ]
}
```

## Migration from Old Setup

If you're upgrading from the previous version:

1. **Set up AWS CLI**:
   ```bash
   aws configure
   ```

2. **Update your `.env` file**:
   ```bash
   # Remove or comment out (keep as fallback)
   # AWS_ACCESS_KEY_ID=...
   # AWS_SECRET_ACCESS_KEY=...
   
   # Add region (required)
   AWS_DEFAULT_REGION=us-east-1
   
   # Add profile if using one
   # AWS_PROFILE=your-profile
   ```

3. **Test the application**:
   ```bash
   python app.py
   ```

4. **Verify in logs** that it shows:
   ```
   AWS Bedrock client initialized successfully using: AWS Profile: default
   ```

## Production Deployment

For production environments:

### AWS EC2/ECS:
1. Create IAM role with Bedrock permissions
2. Attach role to EC2 instance or ECS task
3. Remove AWS credentials from environment variables
4. Application will automatically use the IAM role

### AWS Lambda:
1. Create IAM role with Bedrock permissions
2. Attach role to Lambda function
3. No additional configuration needed

### Other Cloud Providers:
1. Use AWS CLI with appropriate credentials
2. Consider using AWS STS assume role for cross-cloud deployments

## Support

If you encounter issues:

1. Check the application logs for credential source information
2. Verify AWS CLI configuration: `aws configure list`
3. Test AWS access: `aws sts get-caller-identity`
4. Test Bedrock access: `aws bedrock list-foundation-models --region us-east-1`
5. Check the `/api/health` endpoint for credential status
