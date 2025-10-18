#!/usr/bin/env python3
"""
FLUX Project Launcher
Cross-platform script to start both backend and frontend services.
Works on Windows, Mac, and Linux.
"""

import os
import sys
import subprocess
import platform
import time
import signal
from pathlib import Path

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_color(text, color=Colors.BLUE):
    """Print colored text to terminal."""
    print(f"{color}{text}{Colors.END}")

def print_header(text):
    """Print a formatted header."""
    print_color(f"\n{'='*60}", Colors.CYAN)
    print_color(f"  {text}", Colors.BOLD + Colors.CYAN)
    print_color(f"{'='*60}\n", Colors.CYAN)

def check_python_version():
    """Check if Python 3.11+ is installed."""
    version = sys.version_info
    if version < (3, 11):
        print_color(f"❌ Python 3.11+ required. Found: {version.major}.{version.minor}", Colors.RED)
        print_color("Please upgrade Python: https://www.python.org/downloads/", Colors.YELLOW)
        return False
    print_color(f"✅ Python {version.major}.{version.minor}.{version.micro} found", Colors.GREEN)
    return True

def check_node():
    """Check if Node.js is installed."""
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print_color(f"✅ Node.js {version} found", Colors.GREEN)
            return True
    except FileNotFoundError:
        pass
    
    print_color("❌ Node.js not found", Colors.RED)
    print_color("Please install Node.js: https://nodejs.org/", Colors.YELLOW)
    return False

def get_platform_info():
    """Get platform-specific information."""
    system = platform.system()
    
    if system == "Windows":
        return {
            "name": "Windows",
            "venv_activate": "venv\\Scripts\\activate",
            "venv_python": "venv\\Scripts\\python.exe",
            "python_cmd": "python",
            "path_sep": "\\",
        }
    else:  # Mac or Linux
        return {
            "name": system,
            "venv_activate": "venv/bin/activate",
            "venv_python": "venv/bin/python",
            "python_cmd": "python3",
            "path_sep": "/",
        }

def setup_backend(platform_info):
    """Set up backend environment."""
    print_header("Setting up Backend")
    
    backend_dir = Path("backend")
    venv_dir = backend_dir / "venv"
    
    # Create virtual environment if it doesn't exist
    if not venv_dir.exists():
        print_color("📦 Creating virtual environment...", Colors.BLUE)
        subprocess.run(
            [platform_info["python_cmd"], "-m", "venv", str(venv_dir)],
            check=True
        )
        print_color("✅ Virtual environment created", Colors.GREEN)
    else:
        print_color("✅ Virtual environment exists", Colors.GREEN)
    
    # Install dependencies
    requirements_file = backend_dir / "requirements.txt"
    venv_python = backend_dir / platform_info["venv_python"]
    
    print_color("📦 Installing backend dependencies...", Colors.BLUE)
    subprocess.run(
        [str(venv_python), "-m", "pip", "install", "-q", "-r", str(requirements_file)],
        check=True
    )
    print_color("✅ Backend dependencies installed", Colors.GREEN)
    
    # Check for .env file
    env_file = backend_dir / ".env"
    env_example = backend_dir / ".env.example"
    
    if not env_file.exists():
        if env_example.exists():
            print_color("⚠️  .env file not found. Creating from .env.example...", Colors.YELLOW)
            import shutil
            shutil.copy(str(env_example), str(env_file))
            print_color("⚠️  IMPORTANT: Edit backend/.env with your AWS credentials!", Colors.RED)
            print_color("   Press Enter to continue after editing .env...", Colors.YELLOW)
            input()
        else:
            print_color("⚠️  No .env or .env.example found", Colors.YELLOW)
    else:
        print_color("✅ .env file exists", Colors.GREEN)

def setup_frontend():
    """Set up frontend environment."""
    print_header("Setting up Frontend")
    
    frontend_dir = Path("frontend")
    node_modules = frontend_dir / "node_modules"
    
    # Install dependencies
    if not node_modules.exists():
        print_color("📦 Installing frontend dependencies...", Colors.BLUE)
        subprocess.run(
            ["npm", "install"],
            cwd=str(frontend_dir),
            check=True
        )
        print_color("✅ Frontend dependencies installed", Colors.GREEN)
    else:
        print_color("✅ Frontend dependencies exist", Colors.GREEN)
    
    # Check for .env.local
    env_local = frontend_dir / ".env.local"
    
    if not env_local.exists():
        print_color("📝 Creating .env.local...", Colors.BLUE)
        with open(env_local, 'w') as f:
            f.write("NEXT_PUBLIC_API_URL=http://localhost:8000\n")
        print_color("✅ .env.local created", Colors.GREEN)
    else:
        print_color("✅ .env.local exists", Colors.GREEN)

def start_services(platform_info):
    """Start backend and frontend services."""
    print_header("Starting FLUX Services")
    
    backend_dir = Path("backend")
    frontend_dir = Path("frontend")
    venv_python = backend_dir / platform_info["venv_python"]
    
    # Start backend
    print_color("🚀 Starting backend server...", Colors.BLUE)
    backend_process = subprocess.Popen(
        [str(venv_python), "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=str(backend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait a bit for backend to start
    time.sleep(3)
    
    # Start frontend
    print_color("🚀 Starting frontend server...", Colors.BLUE)
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=str(frontend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait a bit for frontend to start
    time.sleep(2)
    
    # Print success message
    print_header("FLUX Services Running!")
    print_color("🌊 FLUX - Research in Motion 🔬\n", Colors.CYAN + Colors.BOLD)
    print_color("Services are running at:", Colors.GREEN)
    print_color("  • Backend API:      http://localhost:8000", Colors.BLUE)
    print_color("  • API Documentation: http://localhost:8000/docs", Colors.BLUE)
    print_color("  • Frontend UI:      http://localhost:3000", Colors.BLUE)
    print_color("\nPress Ctrl+C to stop all services\n", Colors.YELLOW)
    
    # Set up signal handler for graceful shutdown
    def signal_handler(sig, frame):
        print_color("\n\n🛑 Shutting down services...", Colors.YELLOW)
        backend_process.terminate()
        frontend_process.terminate()
        time.sleep(1)
        backend_process.kill()
        frontend_process.kill()
        print_color("✅ Services stopped", Colors.GREEN)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Wait for processes
    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)

def main():
    """Main launcher function."""
    print_color("""
    ███████╗██╗     ██╗   ██╗██╗  ██╗
    ██╔════╝██║     ██║   ██║╚██╗██╔╝
    █████╗  ██║     ██║   ██║ ╚███╔╝ 
    ██╔══╝  ██║     ██║   ██║ ██╔██╗ 
    ██║     ███████╗╚██████╔╝██╔╝ ██╗
    ╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝
    
    Orbital Research Agent Launcher
    """, Colors.CYAN + Colors.BOLD)
    
    # Check prerequisites
    print_header("Checking Prerequisites")
    
    if not check_python_version():
        sys.exit(1)
    
    if not check_node():
        sys.exit(1)
    
    # Get platform info
    platform_info = get_platform_info()
    print_color(f"✅ Platform: {platform_info['name']}", Colors.GREEN)
    
    # Setup
    try:
        setup_backend(platform_info)
        setup_frontend()
    except subprocess.CalledProcessError as e:
        print_color(f"❌ Setup failed: {e}", Colors.RED)
        sys.exit(1)
    except Exception as e:
        print_color(f"❌ Unexpected error: {e}", Colors.RED)
        sys.exit(1)
    
    # Start services
    try:
        start_services(platform_info)
    except Exception as e:
        print_color(f"❌ Failed to start services: {e}", Colors.RED)
        sys.exit(1)

if __name__ == "__main__":
    main()

