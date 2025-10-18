#!/usr/bin/env python3

"""
FLUX Project Cleanup Script
Stops all running FLUX processes (backend on 8000, frontend on 3000)
Cross-platform: Works on Mac, Linux, and Windows
"""

import os
import sys
import platform
import subprocess
import time
from typing import List, Tuple

# ANSI color codes (work on Mac/Linux, Windows 10+)
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'  # No Color
    
    @staticmethod
    def disable():
        """Disable colors on Windows < 10"""
        Colors.RED = Colors.GREEN = Colors.YELLOW = ''
        Colors.BLUE = Colors.CYAN = Colors.MAGENTA = Colors.NC = ''


# Enable ANSI colors on Windows
if platform.system() == 'Windows':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        Colors.disable()


def print_header():
    """Print script header"""
    print()
    print(f"{Colors.BLUE}╔════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.BLUE}║  FLUX Project Cleanup Script          ║{Colors.NC}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════╝{Colors.NC}")
    print()


def find_pids_by_port(port: int) -> List[int]:
    """Find PIDs using a specific port"""
    pids = []
    system = platform.system()
    
    try:
        if system in ['Darwin', 'Linux']:  # Mac or Linux
            result = subprocess.run(
                ['lsof', '-ti', f':{port}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                pids = [int(pid) for pid in result.stdout.strip().split('\n')]
        
        elif system == 'Windows':
            # Use netstat on Windows
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True,
                text=True,
                timeout=5
            )
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if parts:
                        try:
                            pid = int(parts[-1])
                            if pid not in pids:
                                pids.append(pid)
                        except (ValueError, IndexError):
                            pass
    
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        print(f"{Colors.RED}Error finding PIDs on port {port}: {e}{Colors.NC}")
    
    return pids


def get_process_info(pid: int) -> str:
    """Get process information"""
    system = platform.system()
    
    try:
        if system in ['Darwin', 'Linux']:
            result = subprocess.run(
                ['ps', '-p', str(pid), '-o', 'comm='],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.stdout.strip() if result.returncode == 0 else "Unknown"
        
        elif system == 'Windows':
            result = subprocess.run(
                ['tasklist', '/FI', f'PID eq {pid}', '/FO', 'CSV', '/NH'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split(',')
                return parts[0].strip('"') if parts else "Unknown"
    
    except Exception:
        pass
    
    return "Unknown"


def kill_process(pid: int) -> bool:
    """Kill a process by PID"""
    system = platform.system()
    
    try:
        if system in ['Darwin', 'Linux']:
            subprocess.run(['kill', '-9', str(pid)], timeout=5)
        elif system == 'Windows':
            subprocess.run(['taskkill', '/F', '/PID', str(pid)], timeout=5, capture_output=True)
        
        time.sleep(0.5)
        return not is_process_running(pid)
    
    except Exception as e:
        print(f"{Colors.RED}Error killing PID {pid}: {e}{Colors.NC}")
        return False


def is_process_running(pid: int) -> bool:
    """Check if a process is still running"""
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(
                ['tasklist', '/FI', f'PID eq {pid}'],
                capture_output=True,
                text=True,
                timeout=2
            )
            return str(pid) in result.stdout
        else:
            # On Unix-like systems
            os.kill(pid, 0)
            return True
    except (OSError, subprocess.TimeoutExpired):
        return False


def cleanup_port(port: int, service_name: str) -> bool:
    """Clean up processes on a specific port"""
    print(f"{Colors.YELLOW}🔍 Checking port {port} ({service_name})...{Colors.NC}")
    
    pids = find_pids_by_port(port)
    
    if not pids:
        print(f"{Colors.GREEN}✓ Port {port} is free{Colors.NC}")
        print()
        return True
    
    print(f"{Colors.BLUE}Found {len(pids)} process(es) on port {port}:{Colors.NC}")
    for pid in pids:
        process_name = get_process_info(pid)
        print(f"  PID {pid}: {process_name}")
    print()
    
    # Kill processes
    print(f"{Colors.YELLOW}🔨 Killing processes on port {port}...{Colors.NC}")
    success_count = 0
    for pid in pids:
        if kill_process(pid):
            print(f"{Colors.GREEN}✓ Killed PID {pid}{Colors.NC}")
            success_count += 1
        else:
            print(f"{Colors.RED}✗ Failed to kill PID {pid}{Colors.NC}")
    
    # Verify
    time.sleep(1)
    remaining = find_pids_by_port(port)
    if not remaining:
        print(f"{Colors.GREEN}✓ Port {port} is now free{Colors.NC}")
        all_killed = True
    else:
        print(f"{Colors.RED}⚠ {len(remaining)} process(es) still on port {port}{Colors.NC}")
        all_killed = False
    
    print()
    return all_killed


def find_flux_processes() -> List[Tuple[int, str]]:
    """Find FLUX-related processes by name"""
    processes = []
    system = platform.system()
    
    try:
        if system in ['Darwin', 'Linux']:
            # Search for Python, Node, and Next.js processes
            patterns = [
                'python.*main.py',
                'python.*start.py',
                'uvicorn',
                'next-server',
                'next dev',
                'node.*next'
            ]
            
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            for line in result.stdout.split('\n'):
                if 'grep' in line:
                    continue
                for pattern in patterns:
                    if pattern.replace('.*', ' ').replace('.py', '.py') in line.lower():
                        parts = line.split()
                        if len(parts) > 1:
                            try:
                                pid = int(parts[1])
                                cmd = ' '.join(parts[10:])[:60]
                                processes.append((pid, cmd))
                            except (ValueError, IndexError):
                                pass
                        break
        
        elif system == 'Windows':
            # On Windows, look for python.exe and node.exe
            result = subprocess.run(
                ['tasklist', '/FO', 'CSV', '/NH'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            for line in result.stdout.split('\n'):
                if 'python.exe' in line.lower() or 'node.exe' in line.lower():
                    parts = line.split(',')
                    if len(parts) >= 2:
                        try:
                            name = parts[0].strip('"')
                            pid = int(parts[1].strip('"'))
                            processes.append((pid, name))
                        except (ValueError, IndexError):
                            pass
    
    except Exception as e:
        print(f"{Colors.RED}Error finding FLUX processes: {e}{Colors.NC}")
    
    return processes


def cleanup_by_name():
    """Find and kill FLUX-related processes"""
    print(f"{Colors.YELLOW}🔍 Checking for FLUX-related processes...{Colors.NC}")
    
    processes = find_flux_processes()
    
    if not processes:
        print(f"{Colors.GREEN}✓ No FLUX processes found{Colors.NC}")
        print()
        return
    
    print(f"{Colors.BLUE}Found {len(processes)} FLUX-related process(es):{Colors.NC}")
    for pid, cmd in processes[:10]:  # Show max 10
        print(f"  PID {pid}: {cmd}")
    print()
    
    print(f"{Colors.YELLOW}🔨 Killing FLUX processes...{Colors.NC}")
    for pid, cmd in processes:
        if kill_process(pid):
            print(f"{Colors.GREEN}✓ Killed PID {pid}{Colors.NC}")
        else:
            print(f"{Colors.RED}✗ Failed to kill PID {pid}{Colors.NC}")
    
    print()


def final_status():
    """Print final status"""
    print(f"{Colors.BLUE}════════════════════════════════════════{Colors.NC}")
    print(f"{Colors.YELLOW}📊 Final Status Check:{Colors.NC}")
    print()
    
    ports = [8000, 3000]
    all_free = True
    
    for port in ports:
        pids = find_pids_by_port(port)
        if pids:
            print(f"{Colors.RED}✗ Port {port}: STILL IN USE (PIDs: {', '.join(map(str, pids))}){Colors.NC}")
            all_free = False
        else:
            print(f"{Colors.GREEN}✓ Port {port}: FREE{Colors.NC}")
    
    print()
    
    processes = find_flux_processes()
    if processes:
        print(f"{Colors.YELLOW}⚠ Found {len(processes)} remaining FLUX-related process(es){Colors.NC}")
        for pid, cmd in processes[:5]:
            print(f"  PID {pid}: {cmd}")
    else:
        print(f"{Colors.GREEN}✓ No FLUX processes running{Colors.NC}")
    
    print()
    
    if all_free and not processes:
        print(f"{Colors.GREEN}╔════════════════════════════════════════╗{Colors.NC}")
        print(f"{Colors.GREEN}║  Cleanup Complete! ✨                 ║{Colors.NC}")
        print(f"{Colors.GREEN}╚════════════════════════════════════════╝{Colors.NC}")
    else:
        print(f"{Colors.YELLOW}╔════════════════════════════════════════╗{Colors.NC}")
        print(f"{Colors.YELLOW}║  Cleanup partially complete ⚠         ║{Colors.NC}")
        print(f"{Colors.YELLOW}╚════════════════════════════════════════╝{Colors.NC}")
    
    print()
    print(f"{Colors.BLUE}To restart FLUX:{Colors.NC}")
    print(f"  {Colors.YELLOW}python start.py{Colors.NC}")
    print()


def main():
    """Main cleanup routine"""
    print_header()
    
    print(f"{Colors.CYAN}Platform: {platform.system()} {platform.release()}{Colors.NC}")
    print(f"{Colors.CYAN}Python: {sys.version.split()[0]}{Colors.NC}")
    print()
    
    print(f"{Colors.YELLOW}Starting cleanup...{Colors.NC}")
    print()
    
    # Clean up by port
    cleanup_port(8000, "Backend (FastAPI)")
    cleanup_port(3000, "Frontend (Next.js)")
    
    # Clean up by process name
    cleanup_by_name()
    
    # Final verification
    final_status()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Cleanup interrupted by user{Colors.NC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.NC}")
        sys.exit(1)

