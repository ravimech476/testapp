from fastapi import APIRouter, HTTPException, status, Depends, Form
from typing import List, Optional
from app.models.schemas import User, UserCreate, UserUpdate, UserRole
from app.utils.auth import get_current_active_user, check_user_role, get_password_hash
from app.config.database import get_database
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

class PasswordResetRequest(BaseModel):
    new_password: str

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return current_user

@router.get("/", response_model=List[User])
async def get_all_users(
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(check_user_role([UserRole.ADMIN]))
):
    """Get all users (Admin only) with optional filters"""
    db = await get_database()
    
    # Build filter
    filter_dict = {}
    if role:
        filter_dict["role"] = role
    if is_active is not None:
        filter_dict["is_active"] = is_active
    
    users = []
    async for user in db.users.find(filter_dict).sort("created_at", -1):
        user["_id"] = str(user["_id"])
        users.append(User(**user))
    return users

@router.post("/", response_model=User)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(check_user_role([UserRole.ADMIN]))
):
    """Create a new user (Admin only)"""
    db = await get_database()
    
    # Check if username already exists
    existing_user = await db.users.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )
    
    # Check if email already exists
    existing_email = await db.users.find_one({"email": user_data.email})
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.dict()
    user_dict.pop("password")
    user_dict["hashed_password"] = hashed_password
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = datetime.utcnow()
    
    result = await db.users.insert_one(user_dict)
    
    # Retrieve the created user
    created_user = await db.users.find_one({"_id": result.inserted_id})
    created_user["_id"] = str(created_user["_id"])
    
    return User(**created_user)

@router.get("/{user_id}", response_model=User)
async def get_user_by_id(
    user_id: str,
    current_user: User = Depends(check_user_role([UserRole.ADMIN]))
):
    """Get user by ID (Admin only)"""
    db = await get_database()
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user["_id"] = str(user["_id"])
    return User(**user)

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(check_user_role([UserRole.ADMIN]))
):
    """Update user (Admin only)"""
    db = await get_database()
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    # Check if user exists
    existing_user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prepare update data
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        
        # Check for email uniqueness if email is being updated
        if "email" in update_data and update_data["email"] != existing_user["email"]:
            email_check = await db.users.find_one({"email": update_data["email"]})
            if email_check:
                raise HTTPException(status_code=400, detail="Email already exists")
        
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
    
    # Return updated user
    updated_user = await db.users.find_one({"_id": ObjectId(user_id)})
    updated_user["_id"] = str(updated_user["_id"])
    return User(**updated_user)

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(check_user_role([UserRole.ADMIN]))
):
    """Delete user (Admin only)"""
    db = await get_database()
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    # Cannot delete self
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    # Check if user has open issues assigned or reported
    issues_count = await db.issues.count_documents({
        "$or": [
            {"assigned_to": user_id, "status": {"$nin": ["resolved", "closed"]}},
            {"reported_by": user_id, "status": {"$nin": ["resolved", "closed"]}}
        ]
    })
    
    if issues_count > 0:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete user with open issues. Please resolve or reassign issues first."
        )
    
    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}

@router.get("/role/{role}", response_model=List[User])
async def get_users_by_role(
    role: UserRole,
    current_user: User = Depends(check_user_role([UserRole.ADMIN, UserRole.SAFETY_OFFICER]))
):
    """Get users by role"""
    db = await get_database()
    users = []
    async for user in db.users.find({"role": role, "is_active": True}).sort("full_name", 1):
        user["_id"] = str(user["_id"])
        users.append(User(**user))
    return users

@router.put("/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: str,
    current_user: User = Depends(check_user_role([UserRole.ADMIN]))
):
    """Toggle user active status (Admin only)"""
    db = await get_database()
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")
    
    # Get current user
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Toggle status
    new_status = not user.get("is_active", True)
    
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": new_status, "updated_at": datetime.utcnow()}}
    )
    
    return {
        "message": f"User {'activated' if new_status else 'deactivated'} successfully",
        "is_active": new_status
    }

@router.put("/{user_id}/reset-password")
async def reset_user_password(
    user_id: str,
    password_data: PasswordResetRequest,
    current_user: User = Depends(check_user_role([UserRole.ADMIN]))
):
    """Reset user password (Admin only)"""
    db = await get_database()
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    if len(password_data.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
    
    # Get user
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update password
    hashed_password = get_password_hash(password_data.new_password)
    
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"hashed_password": hashed_password, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Password reset successfully"}

@router.get("/stats/summary")
async def get_user_stats(
    current_user: User = Depends(check_user_role([UserRole.ADMIN]))
):
    """Get user statistics (Admin only)"""
    db = await get_database()
    
    # Count users by role
    stats = {}
    for role in UserRole:
        count = await db.users.count_documents({"role": role, "is_active": True})
        stats[f"{role}_count"] = count
    
    # Total users
    stats["total_active_users"] = await db.users.count_documents({"is_active": True})
    stats["total_inactive_users"] = await db.users.count_documents({"is_active": False})
    stats["total_users"] = await db.users.count_documents({})
    
    return stats
