# Automobile Safety Management System - Backend

This is the backend API for the Automobile Safety Management System built with FastAPI and MongoDB.

## 🔧 Authentication System

This system uses **bcrypt-free authentication** with PBKDF2-SHA256 for password hashing, eliminating compatibility issues with bcrypt versions.

## Features

- User authentication and authorization with JWT tokens
- Role-based access control (Admin, Safety Officer, Maintenance, Employee)
- Machine management
- Issue reporting with photo uploads
- Issue assignment and resolution workflow
- File upload and optimization
- **No bcrypt dependency** - uses built-in Python hashlib

## User Roles & Permissions

### Admin
- Manage all users
- Manage all machines
- Assign issues to maintenance personnel
- Close resolved issues
- View all data

### Safety Officer
- Create safety issues
- Upload photos of issues
- View all machines and issues

### Maintenance Personnel
- View assigned issues
- Update issue status (in progress, resolved)
- Upload resolution photos
- Add resolution notes

### Employee
- View machines
- View own reported issues

## Workflow

1. **Safety Officer** inspects machines and finds issues
2. **Safety Officer** creates issue with photos and details
3. **Admin** validates and assigns issue to **Maintenance** person
4. **Maintenance** person checks, solves issue, takes photos, and marks as resolved
5. **Admin** closes the issue

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- MongoDB (local or cloud)

### 1. Setup Environment

```bash
# Navigate to project directory
cd D:\PROJECTS\automobile_safety_backend

# Run the setup script (recommended)
python setup_no_bcrypt.py
```

### 2. Manual Installation (if setup script fails)

```bash
# Clean up any existing bcrypt installations
pip uninstall bcrypt passlib -y

# Install requirements
pip install -r requirements.txt
```

### 3. Configure Database

Edit the `.env` file:
```bash
# Database Configuration
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=automobile_safety_db

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Start MongoDB

```bash
# If using local MongoDB
mongod

# Or start MongoDB service
# Windows: net start MongoDB
# Linux: sudo systemctl start mongod
# macOS: brew services start mongodb-community
```

### 5. Run the Application

```bash
python main.py
```

The API will be available at: http://localhost:8000

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

## 🔐 Authentication Details

### Password Hashing
- Uses **PBKDF2-SHA256** with 100,000 iterations
- Random 16-byte salt for each password
- Format: `salt:hash_hex`
- No external dependencies required

### JWT Tokens
- Secure token-based authentication
- Configurable expiration time
- Role-based access control

## 📊 Environment Variables

Create a `.env` file with these variables:

```bash
# Database
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=automobile_safety_db

# Security
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=5242880
```

## 🗂️ Directory Structure

```
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies (no bcrypt)
├── setup_no_bcrypt.py     # Setup script
├── .env                   # Environment variables
├── uploads/              # Uploaded files directory
└── app/
    ├── config/          # Configuration files
    │   ├── database.py  # MongoDB connection
    │   └── settings.py  # App settings
    ├── models/          # Pydantic models
    │   └── schemas.py   # Data models
    ├── routers/         # API routes
    │   ├── auth.py      # Authentication endpoints
    │   ├── users.py     # User management
    │   ├── machines.py  # Machine operations
    │   └── issues.py    # Issue management
    └── utils/           # Utility functions
        ├── auth.py      # Authentication logic (no bcrypt)
        └── file_handler.py  # File operations
```

## 🛠️ Development

### Running in Development Mode
```bash
# With auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testing the API
```bash
# Health check
curl http://localhost:8000/api/health

# Test registration
curl -X POST "http://localhost:8000/api/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "admin",
       "password": "admin123",
       "email": "admin@company.com",
       "full_name": "Administrator",
       "role": "admin"
     }'
```

## 📱 Mobile App Integration

Update the Flutter app's API service with your server URL:

```dart
// For local development
static const String baseUrl = 'http://localhost:8000/api';

// For Android emulator
static const String baseUrl = 'http://10.0.2.2:8000/api';

// For your network IP
static const String baseUrl = 'http://YOUR_IP:8000/api';
```

## 🔍 Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   ```bash
   # Check if MongoDB is running
   # Windows: tasklist /fi "imagename eq mongod.exe"
   # Linux/Mac: ps aux | grep mongod
   ```

2. **Import Errors**
   ```bash
   # Reinstall requirements
   pip install -r requirements.txt
   ```

3. **Port Already in Use**
   ```bash
   # Kill process on port 8000
   # Windows: netstat -ano | findstr :8000
   # Linux/Mac: lsof -ti:8000 | xargs kill
   ```

4. **Authentication Issues**
   - The system now uses PBKDF2-SHA256
   - No bcrypt compatibility issues
   - Check JWT secret key configuration

### Reset Database
```javascript
// In MongoDB shell
use automobile_safety_db
db.dropDatabase()
```

## 🚀 Deployment

### Production Checklist
- [ ] Change default SECRET_KEY
- [ ] Configure production MongoDB
- [ ] Set up SSL/HTTPS
- [ ] Configure CORS for your domain
- [ ] Set up reverse proxy (nginx)
- [ ] Configure proper logging
- [ ] Set up monitoring

### Docker Deployment (Optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## 📈 Performance Notes

- PBKDF2-SHA256 with 100k iterations provides strong security
- No bcrypt compilation issues across platforms
- Pure Python implementation - works everywhere
- JWT tokens reduce database lookups

## 🤝 Contributing

1. Follow PEP 8 coding standards
2. Test authentication thoroughly
3. Update documentation for new features
4. Ensure cross-platform compatibility

## 📄 License

This project is proprietary software for automobile industry safety management.

---

**Note**: This version eliminates all bcrypt dependencies while maintaining strong security through PBKDF2-SHA256 password hashing.
