# BA&QA Intelligence Platform — Deployment Guide

## 🚀 Quick Start (Production)

### Option 1: Docker Deployment (Recommended)

```bash
# 1. Build Docker image
docker build -t ba-qa-platform .

# 2. Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/.env.production:/app/.env \
  --name ba-qa-platform \
  ba-qa-platform

# 3. Access the application
open http://localhost:8000
```

### Option 2: Manual Deployment

```bash
# 1. Build React frontend
cd frontend
npm install
npm run build
cd ..

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Set environment variables
cp .env.production .env
# Edit .env with your production values

# 4. Run FastAPI server (serves both API + React SPA)
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **API Keys:**
  - Gemini API key (https://aistudio.google.com/apikey)
  - Anthropic API key (https://console.anthropic.com/)

## 🔧 Configuration

### Environment Variables

Copy `.env.production` to `.env` and configure:

```bash
# Required
GEMINI_API_KEY=your-gemini-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Optional
CORS_ORIGINS=https://your-domain.com
SECRET_KEY=your-secret-key-here
```

### Generate Secret Key

```bash
openssl rand -hex 32
```

## 🌐 Production Deployment

### Deploy to Railway

1. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```

2. Login and deploy:
   ```bash
   railway login
   railway init
   railway up
   ```

3. Set environment variables in Railway dashboard

### Deploy to Fly.io

1. Install Fly CLI:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. Deploy:
   ```bash
   fly launch
   fly deploy
   ```

### Deploy to Google Cloud Run

1. Build and push to Container Registry:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/ba-qa-platform
   ```

2. Deploy:
   ```bash
   gcloud run deploy ba-qa-platform \
     --image gcr.io/PROJECT_ID/ba-qa-platform \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

## 📊 Health Checks

```bash
# API health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

## 🔄 Updates

```bash
# Pull latest code
git pull origin main

# Rebuild frontend
cd frontend && npm run build && cd ..

# Restart server
docker-compose restart
# OR
systemctl restart ba-qa-platform
```

## 📦 Backup & Restore

### Backup

```bash
# Backup SQLite database
cp data/ba_platform.db data/ba_platform.db.backup

# Backup ChromaDB
tar -czf chroma_backup.tar.gz data/chroma_db/
```

### Restore

```bash
# Restore SQLite
cp data/ba_platform.db.backup data/ba_platform.db

# Restore ChromaDB
tar -xzf chroma_backup.tar.gz -C data/
```

## 🐛 Troubleshooting

### Frontend not loading

```bash
# Verify build exists
ls -la frontend/dist

# Rebuild frontend
cd frontend && npm run build && cd ..
```

### API errors

```bash
# Check logs
docker logs ba-qa-platform

# Verify environment variables
docker exec ba-qa-platform env | grep API_KEY
```

### Database errors

```bash
# Reset database
rm data/ba_platform.db
python -m data.database  # Recreate tables
```

## 📈 Performance Tuning

### Gunicorn (Multiple Workers)

```bash
# Install
pip install gunicorn

# Run with 4 workers
gunicorn api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔒 Security Best Practices

1. **Use HTTPS** in production (Let's Encrypt)
2. **Set strong SECRET_KEY**
3. **Restrict CORS_ORIGINS** to your domain
4. **Keep API keys secure** (never commit .env)
5. **Regular backups** of database
6. **Update dependencies** regularly

## 📞 Support

- GitHub Issues: https://github.com/your-org/ba-qa-platform/issues
- Documentation: See docs/MIGRATION_ROADMAP.md
