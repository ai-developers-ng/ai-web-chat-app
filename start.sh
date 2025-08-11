#!/bin/bash

# AI Web Application Startup Script

echo "🚀 Starting AI Web Application..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the ai-web-app directory"
    exit 1
fi

# Backend setup
echo "📦 Setting up backend..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Initialize database
echo "🗄️ Initializing database..."
python init_db.py

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.template .env
    echo "📝 Please edit backend/.env with your AWS credentials before continuing."
    echo "Press Enter when ready to continue..."
    read
fi

# Start backend server in background
echo "🔧 Starting backend server..."
python app.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo "🌐 Starting frontend server..."
cd ../frontend

# Check if backend is running
if curl -s http://localhost:5001/api/health > /dev/null; then
    echo "✅ Backend is running successfully!"
else
    echo "⚠️  Backend might not be running properly. Check the logs above."
fi

# Get the public IP address for external access
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "")
PRIVATE_IP=$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4 2>/dev/null || hostname -I | awk '{print $1}')

# Start frontend server
echo "Starting frontend on http://localhost:8000"
python3 -m http.server 8000 &
FRONTEND_PID=$!

echo ""
echo "🎉 Application is now running!"
echo "📱 Local Frontend: http://localhost:8000"
echo "🔧 Local Backend API: http://localhost:5001"
echo ""
if [ ! -z "$PUBLIC_IP" ]; then
    echo "🌐 External Access URLs:"
    echo "📱 Frontend: http://$PUBLIC_IP:8000"
    echo "🔧 Backend API: http://$PUBLIC_IP:5001"
    echo ""
    echo "⚠️  Make sure your security group allows inbound traffic on ports 5001 and 8000"
else
    echo "🌐 Network Access URLs:"
    echo "📱 Frontend: http://$PRIVATE_IP:8000"
    echo "🔧 Backend API: http://$PRIVATE_IP:5001"
    echo ""
    echo "⚠️  Make sure your firewall allows inbound traffic on ports 5001 and 8000"
fi
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
