#!/bin/bash

# FLUX Launcher Script for Mac/Linux
# Starts both backend and frontend services

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print colored output
print_color() {
    echo -e "${2}${1}${NC}"
}

print_header() {
    echo ""
    print_color "============================================================" "$CYAN"
    print_color "  $1" "$CYAN"
    print_color "============================================================" "$CYAN"
    echo ""
}

# Trap Ctrl+C to kill both processes
cleanup() {
    print_color "\n🛑 Shutting down services..." "$YELLOW"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
    print_color "✅ Services stopped" "$GREEN"
    exit 0
}

trap cleanup INT TERM

print_color "
███████╗██╗     ██╗   ██╗██╗  ██╗
██╔════╝██║     ██║   ██║╚██╗██╔╝
█████╗  ██║     ██║   ██║ ╚███╔╝ 
██╔══╝  ██║     ██║   ██║ ██╔██╗ 
██║     ███████╗╚██████╔╝██╔╝ ██╗
╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝

Orbital Research Agent Launcher (Mac/Linux)
" "$CYAN"

# Check prerequisites
print_header "Checking Prerequisites"

# Check Python
if ! command -v python3 &> /dev/null; then
    print_color "❌ Python 3 not found" "$RED"
    print_color "Install Python 3.11+: https://www.python.org/downloads/" "$YELLOW"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_color "✅ Python $PYTHON_VERSION found" "$GREEN"

# Check Node.js
if ! command -v node &> /dev/null; then
    print_color "❌ Node.js not found" "$RED"
    print_color "Install Node.js: https://nodejs.org/" "$YELLOW"
    exit 1
fi

NODE_VERSION=$(node --version)
print_color "✅ Node.js $NODE_VERSION found" "$GREEN"

# Setup Backend
print_header "Setting up Backend"

cd backend

# Create virtual environment if needed
if [ ! -d "venv" ]; then
    print_color "📦 Creating virtual environment..." "$BLUE"
    python3 -m venv venv
    print_color "✅ Virtual environment created" "$GREEN"
else
    print_color "✅ Virtual environment exists" "$GREEN"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
print_color "📦 Installing backend dependencies..." "$BLUE"
pip install -q -r requirements.txt
print_color "✅ Backend dependencies installed" "$GREEN"

# Check .env file
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_color "⚠️  .env file not found. Creating from .env.example..." "$YELLOW"
        cp .env.example .env
        print_color "⚠️  IMPORTANT: Edit backend/.env with your AWS credentials!" "$RED"
        print_color "   Press Enter to continue after editing .env..." "$YELLOW"
        read
    else
        print_color "⚠️  No .env or .env.example found" "$YELLOW"
    fi
else
    print_color "✅ .env file exists" "$GREEN"
fi

cd ..

# Setup Frontend
print_header "Setting up Frontend"

cd frontend

# Install dependencies
if [ ! -d "node_modules" ]; then
    print_color "📦 Installing frontend dependencies..." "$BLUE"
    npm install
    print_color "✅ Frontend dependencies installed" "$GREEN"
else
    print_color "✅ Frontend dependencies exist" "$GREEN"
fi

# Create .env.local if needed
if [ ! -f ".env.local" ]; then
    print_color "📝 Creating .env.local..." "$BLUE"
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
    print_color "✅ .env.local created" "$GREEN"
else
    print_color "✅ .env.local exists" "$GREEN"
fi

cd ..

# Start services
print_header "Starting FLUX Services"

# Start backend
print_color "🚀 Starting backend server..." "$BLUE"
cd backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
print_color "🚀 Starting frontend server..." "$BLUE"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 2

# Print success message
print_header "FLUX Services Running!"
print_color "🌊 FLUX - Research in Motion 🔬\n" "$CYAN"
print_color "Services are running at:" "$GREEN"
print_color "  • Backend API:       http://localhost:8000" "$BLUE"
print_color "  • API Documentation: http://localhost:8000/docs" "$BLUE"
print_color "  • Frontend UI:       http://localhost:3000" "$BLUE"
echo ""
print_color "Press Ctrl+C to stop all services" "$YELLOW"
echo ""

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID

