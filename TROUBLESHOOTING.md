# 🔧 Bugfixer Troubleshooting Guide

## Common Issues and Solutions

### 1. Internal Server Error (500)

**Symptoms:**
- Dashboard shows "Internal Server Error"
- API endpoints return 500 status

**Common Causes & Solutions:**

#### A. Template File Issues
```bash
# Check if template exists
ls -la bugfixer/templates/dashboard.html

# If missing, the service will show a fallback page
# Solution: Ensure template file exists with correct encoding
```

#### B. Character Encoding Issues
```python
# Fixed in main.py:
with open(template_path, "r", encoding="utf-8") as f:
    return HTMLResponse(content=f.read())
```

#### C. Missing Dependencies
```bash
# Install all required packages
pip install fastapi uvicorn python-decouple GitPython httpx sqlalchemy
```

### 2. Service Won't Start

**Check Python Version:**
```bash
python --version  # Should be 3.11+
```

**Check Port Conflicts:**
```bash
# Windows
netstat -an | findstr :8001

# Linux/Mac
lsof -i :8001
```

**Solution:**
```bash
# Kill existing process or change port in .env
BUGFIXER_PORT=8002
```

### 3. Import Errors

**Module Not Found:**
```bash
# Ensure you're in the right directory
cd /path/to/bugfixer

# Check Python path
python -c "import sys; print(sys.path)"

# Install missing modules
pip install <missing-module>
```

### 4. Database Issues

**SQLite Permission Error:**
```bash
# Check write permissions
ls -la bugfixer.db

# Solution: Ensure directory is writable
chmod 755 .
```

### 5. GitHub Integration Issues

**Invalid Token:**
```bash
# Test your token
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
```

**Repository Access:**
```bash
# Ensure token has correct scopes: repo, pull_requests
```

### 6. Target Application Connection

**Connection Refused:**
```bash
# Check if target app is running
curl http://localhost:8000/api/health/

# Check firewall/network settings
```

## 🚀 Quick Fixes

### Restart Services
```bash
# Kill all processes
pkill -f "python.*bugfixer"
pkill -f "python.*manage.py"

# Restart
python run_sample_app.py &
python run_bugfixer.py &
```

### Reset Database
```bash
rm bugfixer.db
python -c "from bugfixer.models.database import init_db; init_db()"
```

### Check Service Status
```bash
# Test endpoints
curl http://127.0.0.1:8001/api/health
curl http://127.0.0.1:8000/api/health/

# Check logs
python run_bugfixer.py  # Run in foreground to see logs
```

## 🔍 Debugging Steps

### 1. Enable Debug Mode
```env
# In .env file
DEBUG=True
```

### 2. Check Logs
```python
# Add to main.py for more logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 3. Test Individual Components
```bash
python -c "
from bugfixer.core.error_detector import ErrorDetector
import asyncio
async def test():
    detector = ErrorDetector()
    errors = await detector.monitor_application('http://localhost:8000')
    print(f'Found {len(errors)} errors')
    await detector.close()
asyncio.run(test())
"
```

### 4. Validate Configuration
```bash
python -c "
from decouple import config
print('GitHub Token:', config('GITHUB_TOKEN', default='NOT_SET'))
print('Target URL:', config('TARGET_APP_URL', default='NOT_SET'))
"
```

## 📊 Health Check Commands

```bash
# Full system check
python test_bugfixer.py

# Individual service checks
curl http://127.0.0.1:8001/api/health
curl http://127.0.0.1:8000/api/health/

# Test buggy endpoint
curl "http://127.0.0.1:8000/api/divide/?numerator=10&denominator=0"
```

## 🆘 Emergency Reset

If everything fails:

```bash
# 1. Stop all services
pkill -f python

# 2. Clean up
rm -f bugfixer.db
rm -rf __pycache__
rm -rf bugfixer/__pycache__

# 3. Reinstall dependencies
pip uninstall -y fastapi uvicorn
pip install fastapi uvicorn python-decouple GitPython httpx sqlalchemy

# 4. Restart
python run_sample_app.py &
sleep 3
python run_bugfixer.py &
sleep 3
python test_bugfixer.py
```

## 📞 Getting Help

1. **Check the logs** - Run services in foreground to see error messages
2. **Test individual components** - Use the test commands above
3. **Verify configuration** - Ensure .env file is correct
4. **Check network connectivity** - Ensure ports are available
5. **Validate dependencies** - Ensure all packages are installed

## ✅ Success Indicators

- ✅ `curl http://127.0.0.1:8001/api/health` returns 200
- ✅ `curl http://127.0.0.1:8000/api/health/` returns 200  
- ✅ Dashboard loads at http://127.0.0.1:8001
- ✅ API docs available at http://127.0.0.1:8001/docs
- ✅ Test script runs without errors
