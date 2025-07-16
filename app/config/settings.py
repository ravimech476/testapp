import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database
    MONGO_URL: str = os.getenv("MONGO_URL", "mongodb://yelmosatheesh:Reset%40123@93.127.134.137:27017?authSource=admin")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "autosafety")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif"}

settings = Settings()
