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
    echo "❌ Please run this script from the ai-web-chat-app directory"
    exit 1
fi

# ── Build React frontend ───────────────────────────────────────
echo "🌐 Building React frontend..."
cd frontend-new

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

npm run build   # outputs to ../frontend/dist/
cd ..

# ── Backend setup ─────────────────────────────────────────────
echo "📦 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "🗄️ Initializing database..."
python init_db.py

if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.template.new .env
    echo "📝 Please edit backend/.env (set AWS_DEFAULT_REGION and SECRET_KEY) then press Enter."
    read
fi

# ── Start Flask ───────────────────────────────────────────────
# Flask serves BOTH the React build (frontend/dist) AND the /api/* routes.
# There is no separate frontend server needed.
echo "🔧 Starting Flask server..."
python app.py &
BACKEND_PID=$!

sleep 3

if curl -s http://localhost:5001/api/health > /dev/null; then
    echo "✅ Backend is running!"
else
    echo "⚠️  Backend may not have started correctly. Check output above."
fi

PRIVATE_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "localhost")

echo ""
echo "🎉 Application is running!"
echo "   http://$PRIVATE_IP:5001"
echo ""
echo "Press Ctrl+C to stop."

cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $BACKEND_PID 2>/dev/null
    echo "✅ Stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM
wait
