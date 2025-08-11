# Deployment Guide for AI Web Chat App

## Issue Fixed
The application was experiencing connectivity issues when running on an EC2 instance and accessing from external browsers. The frontend was hardcoded to connect to `localhost:5001`, which only works when accessing from the same machine.

## Changes Made

### 1. Frontend Configuration (script.js)
- **Dynamic API URL**: The frontend now automatically detects whether it's running in development (localhost) or production mode
- **Smart Host Detection**: Uses `window.location.hostname` to determine the correct backend URL
- **Development Mode**: Uses `http://localhost:5001/api` when accessed via localhost/127.0.0.1
- **Production Mode**: Uses `http://[current-host]:5001/api` when accessed via external IP

### 2. Backend CORS Configuration (app.py)
- **Enhanced CORS**: Updated to allow connections from any origin for API endpoints
- **Production Ready**: Supports credentials and proper headers for external access
- **Flexible Origins**: Maintains localhost support while allowing external connections

### 3. Start Script Improvements (start.sh)
- **IP Detection**: Automatically detects both public and private IP addresses
- **Clear URLs**: Displays both local and external access URLs
- **Security Reminders**: Shows warnings about firewall/security group configuration

## How It Works

### Frontend URL Resolution
```javascript
const getApiBaseUrl = () => {
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'http://localhost:5001/api';  // Development
    } else {
        return `${protocol}//${hostname}:5001/api`;  // Production
    }
};
```

### Backend CORS Configuration
```python
CORS(app, 
     supports_credentials=True, 
     resources={r"/api/*": {"origins": "*"}},
     allow_headers=['Content-Type', 'Authorization'],
     expose_headers=['*'])
```

## Deployment Steps

### 1. Start the Application
```bash
cd ai-web-chat-app
chmod +x start.sh
./start.sh
```

### 2. Configure Security Groups (AWS EC2)
Ensure your EC2 security group allows inbound traffic on:
- **Port 5001**: Backend API
- **Port 8000**: Frontend server
- **Source**: 0.0.0.0/0 (or restrict to specific IPs as needed)

### 3. Configure Firewall (Other Systems)
```bash
# For Ubuntu/Debian
sudo ufw allow 5001
sudo ufw allow 8000

# For RHEL/CentOS
sudo firewall-cmd --permanent --add-port=5001/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### 4. Access the Application
- **Local Access**: http://localhost:8000
- **External Access**: http://[your-ec2-public-ip]:8000

## Verification

### 1. Check Backend Health
```bash
curl http://localhost:5001/api/health
# Should return: {"status": "healthy", ...}
```

### 2. Test External Access
From your browser, navigate to `http://[ec2-public-ip]:8000`
- The frontend should load without errors
- Check browser console for any connection issues
- The health check should show "Connected to AWS Bedrock successfully!" or appropriate AWS configuration message

### 3. Test API Connectivity
Open browser developer tools and check the Network tab:
- API calls should go to `http://[ec2-public-ip]:5001/api/...`
- No CORS errors should appear in the console

## Troubleshooting

### Common Issues

1. **"Backend not running" error**
   - Check if both ports (5001, 8000) are accessible
   - Verify security group/firewall settings
   - Ensure backend is binding to 0.0.0.0, not just localhost

2. **CORS errors**
   - Backend CORS is now configured to allow all origins
   - If issues persist, check if there are additional proxy/load balancer CORS settings

3. **Connection refused**
   - Verify the backend is running: `ps aux | grep python`
   - Check if ports are listening: `netstat -tlnp | grep -E ':(5001|8000)'`
   - Test local connectivity: `curl http://localhost:5001/api/health`

### Security Considerations

1. **Production Deployment**
   - Consider restricting CORS origins to specific domains
   - Use HTTPS in production
   - Implement proper authentication and rate limiting

2. **Firewall Rules**
   - Restrict port access to necessary IP ranges
   - Consider using a reverse proxy (nginx/Apache) for better security

3. **AWS Security Groups**
   - Use specific IP ranges instead of 0.0.0.0/0 when possible
   - Regularly review and update security group rules

## Additional Notes

- The application now works seamlessly in both development and production environments
- No manual configuration changes needed when switching between local and remote access
- The start script provides clear URLs for easy access
- All existing functionality remains unchanged
