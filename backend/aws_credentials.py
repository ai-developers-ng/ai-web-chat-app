"""
AWS Credentials Management Module

This module provides secure credential management for AWS services,
prioritizing system credentials over environment variables.
"""

import os
import logging
import boto3
from botocore.exceptions import NoCredentialsError, ClientError, ProfileNotFound
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class AWSCredentialManager:
    """
    Manages AWS credentials with multiple fallback options for security.
    
    Priority order:
    1. AWS CLI credentials (~/.aws/credentials)
    2. AWS CLI config (~/.aws/config)
    3. IAM roles (for EC2/ECS deployments)
    4. Environment variables (fallback)
    """
    
    def __init__(self, profile_name: Optional[str] = None, region_name: Optional[str] = None):
        """
        Initialize the credential manager.
        
        Args:
            profile_name: AWS profile name (optional)
            region_name: AWS region (optional)
        """
        self.profile_name = profile_name
        self.region_name = region_name or os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        self._session = None
        self._credentials_source = None
    
    def get_session(self) -> boto3.Session:
        """
        Get or create a boto3 session with proper credentials.
        
        Returns:
            boto3.Session: Configured session
            
        Raises:
            NoCredentialsError: If no valid credentials are found
        """
        if self._session is None:
            self._session = self._create_session()
        return self._session
    
    def _create_session(self) -> boto3.Session:
        """Create a new boto3 session with credential detection."""
        try:
            # Try with profile first if specified
            if self.profile_name:
                logger.info(f"Attempting to use AWS profile: {self.profile_name}")
                session = boto3.Session(
                    profile_name=self.profile_name,
                    region_name=self.region_name
                )
                # Test the credentials
                self._test_credentials(session)
                self._credentials_source = f"AWS Profile: {self.profile_name}"
                logger.info(f"Successfully using AWS profile: {self.profile_name}")
                return session
                
        except (ProfileNotFound, NoCredentialsError) as e:
            logger.warning(f"Profile {self.profile_name} not found or invalid: {e}")
        
        try:
            # Try default credential chain (AWS CLI, IAM roles, etc.)
            logger.info("Attempting to use default AWS credential chain")
            session = boto3.Session(region_name=self.region_name)
            
            # Test the credentials
            self._test_credentials(session)
            
            # Determine the source of credentials
            credentials = session.get_credentials()
            if credentials:
                if hasattr(credentials, 'method'):
                    self._credentials_source = f"AWS Credential Chain: {credentials.method}"
                else:
                    self._credentials_source = "AWS Credential Chain"
                logger.info(f"Successfully using {self._credentials_source}")
                return session
                
        except NoCredentialsError:
            logger.warning("No credentials found in AWS credential chain")
        
        # Fallback to environment variables (least secure)
        try:
            logger.info("Falling back to environment variables")
            aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
            aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            
            if aws_access_key and aws_secret_key:
                session = boto3.Session(
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=self.region_name
                )
                self._test_credentials(session)
                self._credentials_source = "Environment Variables"
                logger.warning("Using environment variables for AWS credentials (less secure)")
                return session
            else:
                logger.error("Environment variables AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY not set")
                
        except NoCredentialsError:
            logger.error("Environment variable credentials are invalid")
        
        # No valid credentials found
        raise NoCredentialsError(
            "No valid AWS credentials found. Please configure credentials using:\n"
            "1. AWS CLI: 'aws configure'\n"
            "2. AWS profiles: 'aws configure --profile <profile-name>'\n"
            "3. IAM roles (for EC2/ECS deployments)\n"
            "4. Environment variables (less secure)"
        )
    
    def _test_credentials(self, session: boto3.Session) -> None:
        """
        Test if the credentials are valid by making a simple AWS call.
        
        Args:
            session: boto3 session to test
            
        Raises:
            NoCredentialsError: If credentials are invalid
        """
        try:
            sts_client = session.client('sts')
            sts_client.get_caller_identity()
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['InvalidUserID.NotFound', 'AccessDenied', 'SignatureDoesNotMatch']:
                raise NoCredentialsError(f"Invalid AWS credentials: {e}")
            raise
    
    def get_bedrock_client(self):
        """
        Get a configured Bedrock runtime client.
        
        Returns:
            boto3 client for bedrock-runtime
        """
        session = self.get_session()
        return session.client('bedrock-runtime', region_name=self.region_name)
    
    def get_credentials_info(self) -> Dict[str, Any]:
        """
        Get information about the current credentials.
        
        Returns:
            Dict containing credential information
        """
        try:
            session = self.get_session()
            sts_client = session.client('sts')
            identity = sts_client.get_caller_identity()
            
            return {
                'source': self._credentials_source,
                'region': self.region_name,
                'account_id': identity.get('Account'),
                'user_id': identity.get('UserId'),
                'arn': identity.get('Arn'),
                'profile': self.profile_name
            }
        except Exception as e:
            logger.error(f"Failed to get credential info: {e}")
            return {
                'source': 'Unknown',
                'region': self.region_name,
                'error': str(e)
            }
    
    def test_bedrock_access(self) -> Dict[str, Any]:
        """
        Test access to AWS Bedrock service.
        
        Returns:
            Dict containing test results
        """
        try:
            bedrock_client = self.get_bedrock_client()
            
            # Try to list foundation models to test access
            response = bedrock_client.list_foundation_models()
            models = response.get('modelSummaries', [])
            
            return {
                'success': True,
                'models_available': len(models),
                'credentials_source': self._credentials_source,
                'region': self.region_name
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            return {
                'success': False,
                'error_code': error_code,
                'error_message': error_message,
                'credentials_source': self._credentials_source,
                'region': self.region_name
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'credentials_source': self._credentials_source,
                'region': self.region_name
            }


# Global credential manager instance
_credential_manager = None

def get_credential_manager(profile_name: Optional[str] = None, region_name: Optional[str] = None) -> AWSCredentialManager:
    """
    Get or create the global credential manager instance.
    
    Args:
        profile_name: AWS profile name (optional)
        region_name: AWS region (optional)
        
    Returns:
        AWSCredentialManager instance
    """
    global _credential_manager
    
    if _credential_manager is None:
        _credential_manager = AWSCredentialManager(profile_name, region_name)
    
    return _credential_manager

def get_bedrock_client():
    """
    Get a configured Bedrock runtime client using secure credentials.
    
    Returns:
        boto3 client for bedrock-runtime
    """
    manager = get_credential_manager()
    return manager.get_bedrock_client()
