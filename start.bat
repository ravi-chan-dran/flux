@echo off
REM FLUX Launcher Script for Windows
REM Starts both backend and frontend services

setlocal enabledelayedexpansion

echo.
echo ===============================================================
echo   FLUX - Orbital Research Agent Launcher (Windows)
echo ===============================================================
echo.

REM Check Python
echo [Checking Prerequisites]
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    echo Please install Python 3.11+: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found
    echo Please install Node.js: https://nodejs.org/
    pause
    exit /b 1
)

for /f %%i in ('node --version') do set NODE_VERSION=%%i
echo [OK] Node.js %NODE_VERSION% found
echo.

REM Setup Backend
echo ===============================================================
echo   Setting up Backend
echo ===============================================================
echo.

cd backend

REM Create virtual environment if needed
if not exist "venv" (
    echo [SETUP] Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment exists
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
echo [SETUP] Installing backend dependencies...
pip install -q -r requirements.txt
echo [OK] Backend dependencies installed

REM Check .env file
if not exist ".env" (
    if exist ".env.example" (
        echo [WARNING] .env file not found. Creating from .env.example...
        copy .env.example .env
        echo.
        echo [IMPORTANT] Edit backend\.env with your AWS credentials!
        echo Press any key to continue after editing .env...
        pause >nul
    ) else (
        echo [WARNING] No .env or .env.example found
    )
) else (
    echo [OK] .env file exists
)

cd ..

REM Setup Frontend
echo.
echo ===============================================================
echo   Setting up Frontend
echo ===============================================================
echo.

cd frontend

REM Install dependencies
if not exist "node_modules" (
    echo [SETUP] Installing frontend dependencies...
    call npm install
    echo [OK] Frontend dependencies installed
) else (
    echo [OK] Frontend dependencies exist
)

REM Create .env.local if needed
if not exist ".env.local" (
    echo [SETUP] Creating .env.local...
    echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local
    echo [OK] .env.local created
) else (
    echo [OK] .env.local exists
)

cd ..

REM Start services
echo.
echo ===============================================================
echo   Starting FLUX Services
echo ===============================================================
echo.

REM Start backend in new window
echo [START] Starting backend server...
start "FLUX Backend" /min cmd /c "cd backend && venv\Scripts\activate && python -m uvicorn main:app --host 0.0.0.0 --port 8000"

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
echo [START] Starting frontend server...
start "FLUX Frontend" /min cmd /c "cd frontend && npm run dev"

REM Wait for frontend to start
timeout /t 2 /nobreak >nul

REM Print success message
echo.
echo ===============================================================
echo   FLUX Services Running!
echo ===============================================================
echo.
echo Services are running at:
echo   - Backend API:       http://localhost:8000
echo   - API Documentation: http://localhost:8000/docs
echo   - Frontend UI:       http://localhost:3000
echo.
echo Services are running in separate windows.
echo Close those windows to stop the services.
echo.
echo Press any key to exit this launcher...
pause >nul

