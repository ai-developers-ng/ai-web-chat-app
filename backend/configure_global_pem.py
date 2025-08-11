import os
import ssl
import certifi

def configure_global_pem():
    # Path to the global.pem file in backend directory
    global_pem_path = os.path.join(os.path.dirname(__file__), 'global.pem')
    
    if not os.path.exists(global_pem_path):
        raise FileNotFoundError(f"global.pem not found at {global_pem_path}")
    
    # Create SSL context with certifi and global.pem
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    ssl_context.load_verify_locations(cafile=global_pem_path)
    
    # Set environment variable to use this combined cert file
    os.environ['SSL_CERT_FILE'] = global_pem_path
    
    print(f"Configured SSL_CERT_FILE with global.pem at {global_pem_path}")

if __name__ == "__main__":
    configure_global_pem()
