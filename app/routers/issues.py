from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from typing import List, Optional
from app.models.schemas import Issue, IssueCreate, IssueUpdate, IssueStatus, IssuePriority, User, UserRole
from app.utils.auth import get_current_active_user, check_user_role
from app.utils.file_handler import save_upload_file
from app.config.database import get_database
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=Issue)
async def create_issue(
    title: str = Form(...),
    description: str = Form(...),
    machine_id: str = Form(...),
    priority: IssuePriority = Form(IssuePriority.MEDIUM),
    photos: List[UploadFile] = File(default=[]),
    current_user: User = Depends(check_user_role([UserRole.SAFETY_OFFICER]))
):
    """Create a new issue (Safety Officer only)"""
    db = await get_database()
    
    # Verify machine exists
    machine = await db.machines.find_one({"machine_id": machine_id})
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Save uploaded photos
    photo_paths = []
    for photo in photos:
        if photo.filename:
            photo_path = await save_upload_file(photo)
            photo_paths.append(photo_path)
    
    issue_dict = {
        "title": title,
        "description": description,
        "machine_id": machine_id,
        "priority": priority,
        "status": IssueStatus.OPEN,
        "reported_by": current_user.id,
        "photos": photo_paths,
        "resolution_photos": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.issues.insert_one(issue_dict)
    
    # Retrieve the created issue
    created_issue = await db.issues.find_one({"_id": result.inserted_id})
    created_issue["_id"] = str(created_issue["_id"])
    
    return Issue(**created_issue)

@router.get("/", response_model=List[Issue])
async def get_all_issues(
    status: Optional[IssueStatus] = None,
    priority: Optional[IssuePriority] = None,
    machine_id: Optional[str] = None,
    assigned_to: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Get all issues with optional filters"""
    db = await get_database()
    
    filter_dict = {}
    if status:
        filter_dict["status"] = status
    if priority:
        filter_dict["priority"] = priority
    if machine_id:
        filter_dict["machine_id"] = machine_id
    if assigned_to:
        filter_dict["assigned_to"] = assigned_to
    
    # If user is not admin or safety officer, only show their assigned issues
    if current_user.role == UserRole.MAINTENANCE:
        filter_dict["assigned_to"] = current_user.id
    elif current_user.role == UserRole.EMPLOYEE:
        filter_dict["reported_by"] = current_user.id
    
    issues = []
    async for issue in db.issues.find(filter_dict).sort("created_at", -1):
        issue["_id"] = str(issue["_id"])
        issues.append(Issue(**issue))
    
    return issues

@router.get("/{issue_id}", response_model=Issue)
async def get_issue_by_id(
    issue_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get issue by ID"""
    db = await get_database()
    
    if not ObjectId.is_valid(issue_id):
        raise HTTPException(status_code=400, detail="Invalid issue ID")
    
    issue = await db.issues.find_one({"_id": ObjectId(issue_id)})
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # Check access permissions
    if (current_user.role in [UserRole.MAINTENANCE] and 
        issue.get("assigned_to") != current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if (current_user.role == UserRole.EMPLOYEE and 
        issue.get("reported_by") != current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    issue["_id"] = str(issue["_id"])
    return Issue(**issue)

@router.put("/{issue_id}/assign", response_model=Issue)
async def assign_issue(
    issue_id: str,
    assigned_to: str = Form(...),
    current_user: User = Depends(check_user_role([UserRole.ADMIN]))
):
    """Assign issue to maintenance person (Admin only)"""
    db = await get_database()
    
    if not ObjectId.is_valid(issue_id):
        raise HTTPException(status_code=400, detail="Invalid issue ID")
    
    # Check if issue exists
    issue = await db.issues.find_one({"_id": ObjectId(issue_id)})
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # Check if assigned user exists and is maintenance
    assigned_user = await db.users.find_one({"_id": ObjectId(assigned_to)})
    if not assigned_user:
        raise HTTPException(status_code=404, detail="Assigned user not found")
    
    if assigned_user["role"] != UserRole.MAINTENANCE:
        raise HTTPException(status_code=400, detail="Can only assign to maintenance personnel")
    
    # Update issue
    update_data = {
        "assigned_to": assigned_to,
        "status": IssueStatus.ASSIGNED,
        "updated_at": datetime.utcnow()
    }
    
    await db.issues.update_one(
        {"_id": ObjectId(issue_id)},
        {"$set": update_data}
    )
    
    # Return updated issue
    updated_issue = await db.issues.find_one({"_id": ObjectId(issue_id)})
    updated_issue["_id"] = str(updated_issue["_id"])
    return Issue(**updated_issue)

@router.put("/{issue_id}/resolve", response_model=Issue)
async def resolve_issue(
    issue_id: str,
    resolution_notes: str = Form(...),
    resolution_photos: List[UploadFile] = File(default=[]),
    current_user: User = Depends(check_user_role([UserRole.MAINTENANCE]))
):
    """Resolve issue (Maintenance only)"""
    db = await get_database()
    
    if not ObjectId.is_valid(issue_id):
        raise HTTPException(status_code=400, detail="Invalid issue ID")
    
    # Check if issue exists and is assigned to current user
    issue = await db.issues.find_one({"_id": ObjectId(issue_id)})
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    if issue.get("assigned_to") != current_user.id:
        raise HTTPException(status_code=403, detail="Issue not assigned to you")
    
    if issue["status"] in [IssueStatus.RESOLVED, IssueStatus.CLOSED]:
        raise HTTPException(status_code=400, detail="Issue already resolved/closed")
    
    # Save resolution photos
    resolution_photo_paths = []
    for photo in resolution_photos:
        if photo.filename:
            photo_path = await save_upload_file(photo)
            resolution_photo_paths.append(photo_path)
    
    # Update issue
    update_data = {
        "status": IssueStatus.RESOLVED,
        "resolution_notes": resolution_notes,
        "resolution_photos": resolution_photo_paths,
        "resolved_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.issues.update_one(
        {"_id": ObjectId(issue_id)},
        {"$set": update_data}
    )
    
    # Return updated issue
    updated_issue = await db.issues.find_one({"_id": ObjectId(issue_id)})
    updated_issue["_id"] = str(updated_issue["_id"])
    return Issue(**updated_issue)

@router.put("/{issue_id}/close", response_model=Issue)
async def close_issue(
    issue_id: str,
    current_user: User = Depends(check_user_role([UserRole.ADMIN]))
):
    """Close resolved issue (Admin only)"""
    db = await get_database()
    
    if not ObjectId.is_valid(issue_id):
        raise HTTPException(status_code=400, detail="Invalid issue ID")
    
    # Check if issue exists and is resolved
    issue = await db.issues.find_one({"_id": ObjectId(issue_id)})
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    if issue["status"] != IssueStatus.RESOLVED:
        raise HTTPException(status_code=400, detail="Can only close resolved issues")
    
    # Update issue
    update_data = {
        "status": IssueStatus.CLOSED,
        "updated_at": datetime.utcnow()
    }
    
    await db.issues.update_one(
        {"_id": ObjectId(issue_id)},
        {"$set": update_data}
    )
    
    # Return updated issue
    updated_issue = await db.issues.find_one({"_id": ObjectId(issue_id)})
    updated_issue["_id"] = str(updated_issue["_id"])
    return Issue(**updated_issue)

@router.put("/{issue_id}/status", response_model=Issue)
async def update_issue_status(
    issue_id: str,
    status: IssueStatus = Form(...),
    current_user: User = Depends(get_current_active_user)
):
    """Update issue status"""
    db = await get_database()
    
    if not ObjectId.is_valid(issue_id):
        raise HTTPException(status_code=400, detail="Invalid issue ID")
    
    # Check if issue exists
    issue = await db.issues.find_one({"_id": ObjectId(issue_id)})
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # Check permissions based on status change
    if status == IssueStatus.IN_PROGRESS:
        # Only assigned maintenance can mark as in progress
        if (current_user.role != UserRole.MAINTENANCE or 
            issue.get("assigned_to") != current_user.id):
            raise HTTPException(status_code=403, detail="Only assigned maintenance can mark as in progress")
    
    # Update issue
    update_data = {
        "status": status,
        "updated_at": datetime.utcnow()
    }
    
    await db.issues.update_one(
        {"_id": ObjectId(issue_id)},
        {"$set": update_data}
    )
    
    # Return updated issue
    updated_issue = await db.issues.find_one({"_id": ObjectId(issue_id)})
    updated_issue["_id"] = str(updated_issue["_id"])
    return Issue(**updated_issue)

@router.get("/my/assigned", response_model=List[Issue])
async def get_my_assigned_issues(
    current_user: User = Depends(check_user_role([UserRole.MAINTENANCE]))
):
    """Get issues assigned to current maintenance user"""
    db = await get_database()
    
    issues = []
    async for issue in db.issues.find({"assigned_to": current_user.id}).sort("created_at", -1):
        issue["_id"] = str(issue["_id"])
        issues.append(Issue(**issue))
    
    return issues

@router.get("/my/reported", response_model=List[Issue])
async def get_my_reported_issues(
    current_user: User = Depends(get_current_active_user)
):
    """Get issues reported by current user"""
    db = await get_database()
    
    issues = []
    async for issue in db.issues.find({"reported_by": current_user.id}).sort("created_at", -1):
        issue["_id"] = str(issue["_id"])
        issues.append(Issue(**issue))
    
    return issues
