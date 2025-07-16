# Automobile Safety Management System

Simple FastAPI application for automobile safety management.

## 🚀 Quick Deploy

```bash
# 1. Clone and setup
git clone <your-repo-url>
cd testapp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Create directories
mkdir -p uploads logs

# 3. Start with PM2
pm2 start ecosystem.config.js

# 4. Check status
pm2 list
pm2 logs automobile-safety-api
```

## 📱 Test API

```bash
curl http://localhost:8000/api/health
```

## 📊 PM2 Commands

```bash
pm2 list                    # List processes
pm2 logs automobile-safety-api  # View logs
pm2 restart automobile-safety-api  # Restart
pm2 stop automobile-safety-api     # Stop
```

## 🌐 API Docs

Visit: `http://localhost:8000/docs`
