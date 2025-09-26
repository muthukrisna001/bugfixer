# 🚀 Bugfixer Setup Guide

## Quick Start (5 minutes)

### 1. Install Dependencies
```bash
pip install fastapi uvicorn python-decouple GitPython httpx sqlalchemy Django djangorestframework
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your GitHub token and settings
```

### 3. Start the Services

**Terminal 1 - Sample App (with bugs):**
```bash
python run_sample_app.py
```

**Terminal 2 - Bugfixer Service:**
```bash
python run_bugfixer.py
```

### 4. Test the System
```bash
python test_bugfixer.py
```

### 5. Open Dashboard
Visit: http://localhost:8001

## 🎯 What You Get

### Sample Application (Django)
- **URL**: http://localhost:8000
- **Buggy Endpoints**:
  - `GET /api/divide/` - ZeroDivisionError
  - `POST /api/user-data/` - KeyError  
  - `GET /api/user-by-index/` - IndexError
  - `POST /api/square-root/` - ValueError
  - `GET /api/parse-json/` - JSONDecodeError
  - `GET /api/user-attribute/` - AttributeError
  - `GET /api/type-error/` - TypeError
  - `GET /api/health/` - Working endpoint

### Bugfixer Service (FastAPI)
- **URL**: http://localhost:8001
- **Dashboard**: Web interface for monitoring
- **API**: RESTful endpoints for automation
- **Features**:
  - Automatic bug detection
  - Code analysis with AST parsing
  - AI-powered fix generation
  - Git integration (branch creation, PRs)
  - Real-time monitoring

## 🔧 Configuration for External Projects

### Required Information

1. **GitHub Access**:
   ```env
   GITHUB_TOKEN=your_personal_access_token
   GITHUB_USERNAME=your_username
   GITHUB_REPO_OWNER=repo_owner
   GITHUB_REPO_NAME=repo_name
   ```

2. **Target Application**:
   ```env
   TARGET_APP_URL=https://your-app.com
   TARGET_APP_AUTH_TOKEN=optional_auth_token
   ```

3. **Optional Enhancements**:
   ```env
   OPENAI_API_KEY=your_openai_key  # For enhanced AI fixes
   ```

### GitHub Token Setup
1. Go to https://github.com/settings/tokens
2. Create new token with scopes: `repo`, `pull_requests`
3. Add to `.env` file

## 📊 Testing Individual Components

### Test Bug Detection
```bash
curl "http://localhost:8000/api/divide/?numerator=10&denominator=0"
```

### Test Bugfixer Health
```bash
curl http://localhost:8001/api/health
```

### Start Analysis via API
```bash
curl -X POST "http://localhost:8001/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "project_url": "https://github.com/user/repo.git",
    "target_app_url": "http://localhost:8000",
    "config": {"create_pr": true}
  }'
```

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐
│   Target App    │    │   Bugfixer     │
│  (with bugs)    │◄──►│    Service     │
└─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Error Detector │
                    │  Code Analyzer  │
                    │  Fix Generator  │
                    │  Git Manager    │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   GitHub PR     │
                    │   with Fix      │
                    └─────────────────┘
```

## 🔍 Supported Error Types

- **ZeroDivisionError**: Division by zero
- **KeyError**: Missing dictionary keys
- **IndexError**: List index out of bounds
- **ValueError**: Invalid values (e.g., negative sqrt)
- **TypeError**: Type mismatches
- **AttributeError**: Accessing None attributes
- **JSONDecodeError**: Invalid JSON parsing

## 🚀 Next Steps

1. **For Demo**: Use the provided sample app
2. **For Real Projects**: 
   - Update `.env` with your repository details
   - Configure GitHub token
   - Point to your running application
   - Start analysis from dashboard

## 🛠️ Extending the System

### Add New Error Types
1. Update `ErrorType` enum in `models/schemas.py`
2. Add detection logic in `core/error_detector.py`
3. Implement analysis in `core/analyzer.py`
4. Create fix templates in `core/fix_generator.py`

### Custom Fix Generators
```python
class CustomFixGenerator(FixGenerator):
    async def _generate_custom_fix(self, bug_report, original_code):
        # Your custom logic here
        return FixSuggestion(...)
```

## 📞 Support

- Check logs in terminal outputs
- Verify both services are running
- Ensure correct Python version (3.11+)
- Test individual endpoints manually

## 🎉 Success Indicators

✅ Both services start without errors  
✅ Dashboard loads at http://localhost:8001  
✅ Sample app responds at http://localhost:8000  
✅ Test script runs successfully  
✅ Bug detection finds 7 errors  
✅ Analysis can be started via API
