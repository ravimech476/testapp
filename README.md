# Automobile Safety Management System

A FastAPI-based system to manage safety inspections and issues in the automobile industry.

## 🚀 Features

- **Authentication System** - JWT-based user authentication
- **User Management** - Role-based access control
- **Machine Management** - Track automobile equipment
- **Issue Tracking** - Safety inspection management
- **File Upload** - Image and document handling
- **MongoDB Integration** - Async database operations

## 🛠️ Tech Stack

- **FastAPI** - Modern Python web framework
- **MongoDB** - NoSQL database with Motor (async driver)
- **JWT** - JSON Web Token authentication
- **Uvicorn** - ASGI server
- **PM2** - Process manager for production

## 📋 Requirements

- Python 3.8+
- MongoDB 4.4+
- Node.js (for PM2)

## 🚀 Quick Deploy on Ubuntu Server

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd testapp
```

### 2. Run Deployment Script
```bash
chmod +x deploy.sh
./deploy.sh
```

### 3. Start with PM2
```bash
pm2 start ecosystem.config.js
pm2 list
pm2 logs automobile-safety-api
```

### 4. Setup Auto-Start
```bash
pm2 save
pm2 startup
```

### 5. Verify Deployment
```bash
curl http://localhost:8000/api/health
```

## 🔧 Manual Setup

### 1. Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Update `.env` file with your MongoDB credentials:
```env
MONGO_URL=your_mongodb_connection_string
DATABASE_NAME=autosafety
SECRET_KEY=your-super-secret-key
```

### 4. Run Development Server
```bash
python main.py
```

### 5. Production with PM2
```bash
npm install -g pm2
pm2 start ecosystem.config.js
```

## 📱 API Endpoints

- **GET /** - Root endpoint
- **GET /api/health** - Health check
- **POST /api/auth/login** - User login
- **GET /api/users/** - User management
- **GET /api/machines/** - Machine management  
- **GET /api/issues/** - Issue tracking

## 📖 API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

## 🔐 Security

- JWT token-based authentication
- Password hashing with bcrypt
- CORS configuration
- Environment variable protection

## 📊 Monitoring

```bash
# PM2 Commands
pm2 list              # List all processes
pm2 logs <app-name>    # View logs
pm2 monit             # Real-time monitoring
pm2 restart <app-name> # Restart application
pm2 stop <app-name>    # Stop application
```

## 🗂️ Project Structure

```
testapp/
├── app/
│   ├── config/
│   │   ├── database.py
│   │   └── settings.py
│   ├── models/
│   │   └── schemas.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── machines.py
│   │   └── issues.py
│   └── utils/
│       └── auth.py
├── uploads/
├── logs/
├── main.py
├── requirements.txt
├── ecosystem.config.js
└── .env
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License.
