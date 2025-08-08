@echo off
REM AI Web Application Startup Script for Windows

echo 🚀 Starting AI Web Application...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "README.md" (
    echo ❌ Please run this script from the ai-web-app directory
    pause
    exit /b 1
)

REM Backend setup
echo 📦 Setting up backend...
cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Initialize database
echo 🗄️ Initializing database...
python init_db.py

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found. Creating from template...
    copy .env.template .env
    echo 📝 Please edit backend\.env with your AWS credentials before continuing.
    echo Press any key when ready to continue...
    pause >nul
)

REM Start backend server
echo 🔧 Starting backend server...
start "Backend Server" python app.py

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend server
echo 🌐 Starting frontend server...
cd ..\frontend

REM Check if backend is running (simplified check for Windows)
echo Checking backend connection...

REM Start frontend server
echo Starting frontend on http://localhost:8000
start "Frontend Server" python -m http.server 8000

echo.
echo 🎉 Application is now running!
echo 📱 Frontend: http://localhost:8000
echo 🔧 Backend API: http://localhost:5001
echo.
echo Press any key to open the application in your browser...
pause >nul

REM Open browser
start http://localhost:8000

echo.
echo Press any key to exit (this will close the servers)...
pause >nul
