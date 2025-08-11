
"""
SSL Configuration Module for AWS Bedrock SSL Validation
Handles SSL certificate validation using global.pem instead of disabling SSL
"""

import ssl
import certifi
import os
from pathlib import Path

def configure_ssl_with_global_pem():
    """
    Configure SSL to use global.pem for certificate validation
    This provides proper SSL validation instead of disabling it
    """
    # Get the path to global.pem
    backend_dir = Path(__file__).parent
    global_pem_path = backend_dir / "global.pem"
    
    if global_pem_path.exists():
        # Use global.pem for SSL certificate validation
        os.environ['SSL_CERT_FILE'] = str(global_pem_path)
        
        # Create SSL context with global.pem
        ssl_context = ssl.create_default_context(cafile=str(global_pem_path))
        
        # Also load certifi certificates as fallback
        ssl_context.load_verify_locations(cafile=certifi.where())
        
        print(f"✅ SSL configured with global.pem: {global_pem_path}")
        return ssl_context
    else:
        # Fallback to certifi certificates
        print("⚠️ global.pem not found, using certifi certificates")
        os.environ['SSL_CERT_FILE'] = certifi.where()
        return ssl.create_default_context(cafile=certifi.where())

def get_ssl_context():
    """Get the configured SSL context for AWS services"""
    return configure_ssl_with_global_pem()

# Configure SSL on import
ssl_context = get_ssl_context()
