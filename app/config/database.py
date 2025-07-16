import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None

db = Database()

async def get_database() -> AsyncIOMotorDatabase:
    return db.database

async def connect_to_mongo():
    """Create database connection"""
    # MongoDB connection string - update as needed
    MONGO_URL = os.getenv("MONGO_URL", "mongodb://yelmosatheesh:Reset%40123@93.127.134.137:27017?authSource=admin")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "autosafety")
    
    db.client = AsyncIOMotorClient(MONGO_URL)
    db.database = db.client[DATABASE_NAME]
    
    # Test connection
    try:
        await db.client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB!")
