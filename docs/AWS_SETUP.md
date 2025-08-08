# AWS Bedrock Setup Guide

## Prerequisites
1. AWS Account with appropriate permissions
2. AWS CLI installed
3. Python 3.8+ installed

## Step 1: Install AWS CLI
```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Windows
# Download and run the AWS CLI MSI installer from AWS website
```

## Step 2: Configure AWS Credentials
```bash
aws configure
```
Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., us-east-1)
- Default output format (json)

## Step 3: Enable AWS Bedrock Models
1. Go to AWS Console → Bedrock → Model Access
2. Request access to the following models:
   - Anthropic Claude 3 Sonnet
   - Amazon Titan Image Generator
   - Any other models you want to use

## Step 4: Set Up IAM Permissions
Create an IAM policy with the following permissions:
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

## Step 5: Environment Variables (Optional)
Create a `.env` file in the backend directory:
```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
```

## Step 6: Test AWS Connection
```bash
aws bedrock list-foundation-models --region us-east-1
```

## Troubleshooting
- If you get permission errors, check your IAM policies
- If models are not available, ensure you've requested access in the Bedrock console
- For region issues, make sure Bedrock is available in your selected region
