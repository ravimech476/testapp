import os
import uuid
from fastapi import UploadFile, HTTPException
from app.config.settings import settings
from PIL import Image
import shutil

async def save_upload_file(upload_file: UploadFile) -> str:
    """Save uploaded file and return the file path"""
    
    # Check file extension
    file_extension = os.path.splitext(upload_file.filename)[1].lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # Create upload directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Save the file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        # Optimize image if it's an image file
        if file_extension in [".jpg", ".jpeg", ".png"]:
            optimize_image(file_path)
        
        return file_path
    
    except Exception as e:
        # Clean up if something went wrong
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")

def optimize_image(file_path: str, max_size: tuple = (1024, 1024), quality: int = 85):
    """Optimize image size and quality"""
    try:
        with Image.open(file_path) as img:
            # Convert to RGB if necessary
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # Resize if image is too large
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save with optimization
            img.save(file_path, optimize=True, quality=quality)
    
    except Exception as e:
        print(f"Could not optimize image {file_path}: {str(e)}")

def delete_file(file_path: str) -> bool:
    """Delete a file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Could not delete file {file_path}: {str(e)}")
        return False
