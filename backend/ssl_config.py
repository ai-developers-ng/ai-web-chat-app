
# Add to your Python code to handle SSL issues
import ssl
import certifi
import os

# Method 1: Use certifi certificates
os.environ['SSL_CERT_FILE'] = certifi.where()

# Method 2: Disable SSL verification (development only)
# ssl._create_default_https_context = ssl._create_unverified_context

# Method 3: Custom SSL context
ssl_context = ssl.create_default_context(cafile=certifi.where())
