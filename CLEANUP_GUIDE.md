# FLUX Cleanup Scripts Guide

This guide explains how to use the cleanup scripts to stop all FLUX project processes.

## Scripts Available

### 1. `cleanup.py` (Recommended - Cross-platform)

**Python script that works on Mac, Linux, and Windows**

```bash
python3 cleanup.py
```

### 2. `cleanup.sh` (Mac/Linux only)

**Bash script for Unix-like systems**

```bash
./cleanup.sh
# or
bash cleanup.sh
```

## What They Do

Both scripts will:

1. ✅ **Check ports 8000 and 3000** for running processes
2. ✅ **Display process information** before killing them
3. ✅ **Kill all FLUX-related processes**:
   - Backend (FastAPI/Uvicorn on port 8000)
   - Frontend (Next.js on port 3000)
   - Start script processes
4. ✅ **Verify cleanup** and show final status
5. ✅ **Provide restart instructions**

## Usage

### Quick Cleanup

From the project root:

```bash
# Python version (works everywhere)
python3 cleanup.py

# Bash version (Mac/Linux)
./cleanup.sh
```

### Sample Output

```
╔════════════════════════════════════════╗
║  FLUX Project Cleanup Script          ║
╚════════════════════════════════════════╝

Platform: Darwin 24.6.0
Python: 3.13.3

Starting cleanup...

🔍 Checking port 8000 (Backend (FastAPI))...
Found 2 process(es) on port 8000:
  PID 95980: python main.py
  PID 96005: uvicorn

🔨 Killing processes on port 8000...
✓ Killed PID 95980
✓ Killed PID 96005
✓ Port 8000 is now free

🔍 Checking port 3000 (Frontend (Next.js))...
Found 1 process(es) on port 3000:
  PID 99098: next-server (v14.2.0)

🔨 Killing processes on port 3000...
✓ Killed PID 99098
✓ Port 3000 is now free

🔍 Checking for FLUX-related processes...
✓ No FLUX processes found

════════════════════════════════════════
📊 Final Status Check:

✓ Port 8000: FREE
✓ Port 3000: FREE
✓ No FLUX processes running

╔════════════════════════════════════════╗
║  Cleanup Complete! ✨                 ║
╚════════════════════════════════════════╝

To restart FLUX:
  python start.py
```

## When to Use

### Use cleanup scripts when:

- ✅ You need to fully stop FLUX to free ports
- ✅ Processes are stuck or not responding
- ✅ You want to restart fresh
- ✅ Port 8000 or 3000 is already in use
- ✅ Before running tests or making changes
- ✅ Before shutting down your computer

### Don't use cleanup scripts when:

- ❌ FLUX is actively running research (let it complete first)
- ❌ You just want to temporarily pause (use Ctrl+C instead)

## Platform-Specific Notes

### Mac (Darwin)

- Uses `lsof` to find processes by port
- Uses `ps aux` to find processes by name
- Uses `kill -9` for forceful termination
- ✅ Both scripts work

### Linux

- Uses same commands as Mac
- ✅ Both scripts work

### Windows

- Python script uses `netstat` and `tasklist`
- Python script uses `taskkill /F` for termination
- ✅ Only `cleanup.py` works on Windows
- ❌ `cleanup.sh` requires WSL or Git Bash

## Common Issues

### Script Not Executable

```bash
# Fix for cleanup.sh
chmod +x cleanup.sh

# Or just use bash
bash cleanup.sh
```

### Python Command Not Found

```bash
# Try python3 instead
python3 cleanup.py

# Or use full path
/usr/bin/python3 cleanup.py
```

### Permission Denied

```bash
# On Mac/Linux, you might need sudo for system processes
sudo python3 cleanup.py
```

### Processes Still Running

If processes remain after cleanup:

1. **Check the final status output** - it will show remaining processes
2. **Try running cleanup again** - sometimes processes take time to die
3. **Manual cleanup**:

```bash
# Find processes on a port
lsof -ti:8000        # Mac/Linux
netstat -ano | findstr :8000   # Windows

# Kill by PID
kill -9 <PID>        # Mac/Linux
taskkill /F /PID <PID>   # Windows
```

## Integration with Other Scripts

### Before Running Tests

```bash
# Clean up first
python3 cleanup.py

# Then run tests
cd backend
pytest
```

### Before Deployment

```bash
# Clean up local instances
python3 cleanup.py

# Then deploy
# ... deployment commands
```

### In CI/CD Pipeline

```yaml
# GitHub Actions example
- name: Cleanup before tests
  run: python3 cleanup.py
  
- name: Run tests
  run: pytest
```

## Advanced Usage

### Cleanup Specific Port Only

Edit the script to comment out ports you want to keep:

```python
# In cleanup.py, modify:
cleanup_port(8000, "Backend (FastAPI)")
# cleanup_port(3000, "Frontend (Next.js)")  # Comment out to skip
```

### Verbose Mode

Add debug output by uncommenting debug lines in the scripts.

### Dry Run

To see what would be killed without actually killing:

```python
# In cleanup.py, comment out the kill_process() calls
# Just prints what it would kill
```

## Comparison

| Feature | cleanup.py | cleanup.sh |
|---------|------------|------------|
| **Cross-platform** | ✅ Yes (Mac/Linux/Windows) | ❌ Mac/Linux only |
| **Port checking** | ✅ Yes | ✅ Yes |
| **Process name search** | ✅ Yes | ✅ Yes |
| **Colorized output** | ✅ Yes | ✅ Yes |
| **Detailed logging** | ✅ Yes | ✅ Yes |
| **Dependencies** | Python 3.6+ | Bash, lsof, ps |
| **Speed** | Medium | Fast |
| **Recommended** | ✅ Yes | For Mac/Linux users |

## Troubleshooting

### Colors Don't Show

```bash
# Disable colors manually or script will auto-detect
export NO_COLOR=1
python3 cleanup.py
```

### Script Hangs

- Press `Ctrl+C` to interrupt
- Check if you have permission to kill processes
- Try with `sudo` on Mac/Linux

### Wrong Processes Killed

- Scripts only target:
  - Processes on ports 8000 and 3000
  - Python processes running `main.py` or `start.py`
  - Next.js and Uvicorn processes
- Other processes are safe

## Quick Reference

```bash
# ✅ RECOMMENDED - Works everywhere
python3 cleanup.py

# Mac/Linux only
./cleanup.sh

# Check if ports are free (after cleanup)
lsof -i:8000,3000             # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Restart FLUX
python start.py
```

## Files

- `cleanup.py` - Cross-platform Python script (256 lines)
- `cleanup.sh` - Mac/Linux bash script (180 lines)
- `CLEANUP_GUIDE.md` - This documentation

## Updates

Both scripts are regularly updated to:
- Support new process types
- Improve cross-platform compatibility
- Add better error handling
- Enhance output formatting

Last updated: October 18, 2025

---

**Need help?** Check the terminal output - it provides detailed information about what's happening at each step.

