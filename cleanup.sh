#!/bin/bash

################################################################################
# FLUX Project Cleanup Script
# 
# Stops all running FLUX processes (backend on 8000, frontend on 3000)
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  FLUX Project Cleanup Script          ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo ""

# Function to check and kill processes on a port
cleanup_port() {
    local port=$1
    local service_name=$2
    
    echo -e "${YELLOW}🔍 Checking port ${port} (${service_name})...${NC}"
    
    # Find PIDs on this port
    pids=$(lsof -ti:${port} 2>/dev/null)
    
    if [ -z "$pids" ]; then
        echo -e "${GREEN}✓ Port ${port} is free${NC}"
        echo ""
        return 0
    fi
    
    # Show what's running
    echo -e "${BLUE}Found processes on port ${port}:${NC}"
    lsof -i:${port} 2>/dev/null | head -10
    echo ""
    
    # Kill the processes
    echo -e "${YELLOW}🔨 Killing processes on port ${port}...${NC}"
    for pid in $pids; do
        if kill -0 $pid 2>/dev/null; then
            kill -9 $pid 2>/dev/null
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✓ Killed PID ${pid}${NC}"
            else
                echo -e "${RED}✗ Failed to kill PID ${pid}${NC}"
            fi
        fi
    done
    
    # Verify port is free
    sleep 1
    remaining=$(lsof -ti:${port} 2>/dev/null)
    if [ -z "$remaining" ]; then
        echo -e "${GREEN}✓ Port ${port} is now free${NC}"
    else
        echo -e "${RED}⚠ Some processes may still be running on port ${port}${NC}"
    fi
    echo ""
}

# Function to find and kill FLUX-related processes by name
cleanup_by_name() {
    echo -e "${YELLOW}🔍 Checking for FLUX-related processes...${NC}"
    
    # Find Python processes running main.py
    python_pids=$(ps aux | grep -E "python.*main.py|uvicorn.*main" | grep -v grep | awk '{print $2}')
    if [ ! -z "$python_pids" ]; then
        echo -e "${BLUE}Found Python backend processes:${NC}"
        ps aux | grep -E "python.*main.py|uvicorn.*main" | grep -v grep | head -5
        echo ""
        for pid in $python_pids; do
            kill -9 $pid 2>/dev/null
            echo -e "${GREEN}✓ Killed Python backend PID ${pid}${NC}"
        done
        echo ""
    fi
    
    # Find Next.js processes
    nextjs_pids=$(ps aux | grep -E "next-server|next dev|node.*next" | grep -v grep | awk '{print $2}')
    if [ ! -z "$nextjs_pids" ]; then
        echo -e "${BLUE}Found Next.js frontend processes:${NC}"
        ps aux | grep -E "next-server|next dev|node.*next" | grep -v grep | head -5
        echo ""
        for pid in $nextjs_pids; do
            kill -9 $pid 2>/dev/null
            echo -e "${GREEN}✓ Killed Next.js frontend PID ${pid}${NC}"
        done
        echo ""
    fi
    
    # Find start.py processes
    start_pids=$(ps aux | grep "python.*start.py" | grep -v grep | awk '{print $2}')
    if [ ! -z "$start_pids" ]; then
        echo -e "${BLUE}Found start.py launcher processes:${NC}"
        ps aux | grep "python.*start.py" | grep -v grep
        echo ""
        for pid in $start_pids; do
            kill -9 $pid 2>/dev/null
            echo -e "${GREEN}✓ Killed start.py PID ${pid}${NC}"
        done
        echo ""
    fi
}

# Main cleanup
echo -e "${YELLOW}Starting cleanup...${NC}"
echo ""

# Clean up by port
cleanup_port 8000 "Backend (FastAPI)"
cleanup_port 3000 "Frontend (Next.js)"

# Clean up by process name (catches any stragglers)
cleanup_by_name

# Final verification
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${YELLOW}📊 Final Status Check:${NC}"
echo ""

# Check ports
for port in 8000 3000; do
    if lsof -i:${port} >/dev/null 2>&1; then
        echo -e "${RED}✗ Port ${port}: STILL IN USE${NC}"
        lsof -i:${port} 2>/dev/null | head -3
    else
        echo -e "${GREEN}✓ Port ${port}: FREE${NC}"
    fi
done

echo ""

# Check for any remaining FLUX processes
remaining=$(ps aux | grep -E "python.*main.py|uvicorn|next-server|next dev|python.*start.py" | grep -v grep | wc -l)
if [ $remaining -gt 0 ]; then
    echo -e "${YELLOW}⚠ Found ${remaining} remaining FLUX-related processes:${NC}"
    ps aux | grep -E "python.*main.py|uvicorn|next-server|next dev|python.*start.py" | grep -v grep | head -5
else
    echo -e "${GREEN}✓ No FLUX processes running${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Cleanup Complete! ✨                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}To restart FLUX:${NC}"
echo -e "  ${YELLOW}python start.py${NC}"
echo ""
echo -e "${BLUE}Or manually:${NC}"
echo -e "  ${YELLOW}cd backend && source venv/bin/activate && python main.py${NC}"
echo -e "  ${YELLOW}cd frontend && npm run dev${NC}"
echo ""

