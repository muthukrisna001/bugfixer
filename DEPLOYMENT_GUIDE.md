# 🚀 Bugfixer Deployment Guide

## Deployment Options

### 1. **Cloud Server (AWS/GCP/Azure)**

**Setup on Ubuntu Server:**
```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip git

# Clone your bugfixer
git clone https://github.com/yourusername/bugfixer.git
cd bugfixer

# Install requirements
pip3 install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your GitHub token, etc.

# Run with systemd service
sudo nano /etc/systemd/system/bugfixer.service
```

**Systemd Service File:**
```ini
[Unit]
Description=Bugfixer Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/bugfixer
Environment=PATH=/home/ubuntu/.local/bin
ExecStart=/usr/bin/python3 run_bugfixer.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Start the service:**
```bash
sudo systemctl enable bugfixer
sudo systemctl start bugfixer
sudo systemctl status bugfixer
```

### 2. **Docker Container**

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["python", "run_bugfixer.py"]
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  bugfixer:
    build: .
    ports:
      - "8001:8001"
    environment:
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - BUGFIXER_HOST=0.0.0.0
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

**Deploy:**
```bash
docker-compose up -d
```

### 3. **Kubernetes Cluster**

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bugfixer
spec:
  replicas: 2
  selector:
    matchLabels:
      app: bugfixer
  template:
    metadata:
      labels:
        app: bugfixer
    spec:
      containers:
      - name: bugfixer
        image: your-registry/bugfixer:latest
        ports:
        - containerPort: 8001
        env:
        - name: GITHUB_TOKEN
          valueFrom:
            secretKeyRef:
              name: bugfixer-secrets
              key: github-token
---
apiVersion: v1
kind: Service
metadata:
  name: bugfixer-service
spec:
  selector:
    app: bugfixer
  ports:
  - port: 80
    targetPort: 8001
  type: LoadBalancer
```

### 4. **Serverless (AWS Lambda)**

**serverless.yml:**
```yaml
service: bugfixer

provider:
  name: aws
  runtime: python3.11
  environment:
    GITHUB_TOKEN: ${env:GITHUB_TOKEN}

functions:
  api:
    handler: lambda_handler.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
    timeout: 30
```

## 🌐 **Access Patterns**

### **Scenario 1: Company Internal Tool**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Developer     │    │   Bugfixer     │    │   GitHub        │
│   Workstation   │───►│   Server        │───►│   Repository    │
│                 │    │   (Internal)    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Target Apps    │
                    │  (Staging/Prod) │
                    └─────────────────┘
```

### **Scenario 2: SaaS Service**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Customer      │    │   Bugfixer     │    │   Customer      │
│   Dashboard     │───►│   Cloud Service │───►│   GitHub        │
│                 │    │   (Public)      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Customer Apps  │
                    │  (Any URL)      │
                    └─────────────────┘
```

### **Scenario 3: CI/CD Integration**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Git Push      │    │   CI/CD         │    │   Bugfixer     │
│                 │───►│   Pipeline      │───►│   Service       │
│                 │    │   (GitHub       │    │                 │
└─────────────────┘    │    Actions)     │    └─────────────────┘
                       └─────────────────┘
```

## 🔧 **Configuration for Different Environments**

### **Development (.env.dev)**
```env
BUGFIXER_HOST=127.0.0.1
BUGFIXER_PORT=8001
DEBUG=True
TARGET_APP_URL=http://localhost:8000
```

### **Production (.env.prod)**
```env
BUGFIXER_HOST=0.0.0.0
BUGFIXER_PORT=8001
DEBUG=False
TARGET_APP_URL=https://your-production-app.com
DATABASE_URL=postgresql://user:pass@db:5432/bugfixer
```

### **Cloud (.env.cloud)**
```env
BUGFIXER_HOST=0.0.0.0
BUGFIXER_PORT=8001
DEBUG=False
DATABASE_URL=sqlite:///./data/bugfixer.db
GITHUB_TOKEN=${GITHUB_TOKEN}  # From environment
```

## 🚀 **Quick Deploy Commands**

### **AWS EC2:**
```bash
# Launch instance
aws ec2 run-instances --image-id ami-0abcdef1234567890 --instance-type t3.micro

# SSH and setup
ssh -i key.pem ubuntu@your-instance-ip
git clone https://github.com/yourusername/bugfixer.git
cd bugfixer && ./deploy.sh
```

### **Google Cloud Run:**
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/bugfixer
gcloud run deploy --image gcr.io/PROJECT-ID/bugfixer --platform managed
```

### **Heroku:**
```bash
# Create app
heroku create your-bugfixer-app

# Set environment variables
heroku config:set GITHUB_TOKEN=your_token

# Deploy
git push heroku main
```

## 🔒 **Security Considerations**

### **Environment Variables:**
- Never commit `.env` files
- Use cloud secret managers
- Rotate GitHub tokens regularly

### **Network Security:**
- Use HTTPS in production
- Implement rate limiting
- Add authentication for public deployments

### **Access Control:**
```python
# Add to main.py for authentication
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.middleware("http")
async def authenticate(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        # Add your authentication logic
        pass
    response = await call_next(request)
    return response
```

## 📊 **Monitoring & Logging**

### **Add Logging:**
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In your endpoints
logger.info(f"Analysis started for {project_url}")
```

### **Health Checks:**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

## 🎯 **Recommended Setup**

**For Small Teams:** Docker on a single cloud server
**For Companies:** Kubernetes cluster with load balancing  
**For SaaS:** Serverless with auto-scaling
**For CI/CD:** GitHub Actions integration
