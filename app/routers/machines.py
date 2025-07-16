from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from app.models.schemas import Machine, MachineCreate, MachineUpdate, MachineStatus, User, UserRole
from app.utils.auth import get_current_active_user, check_user_role
from app.config.database import get_database
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=Machine)
async def create_machine(
    machine: MachineCreate,
    current_user: User = Depends(check_user_role([UserRole.ADMIN]))
):
    """Create a new machine (Admin only)"""
    db = await get_database()
    
    # Check if machine_id already exists
    existing_machine = await db.machines.find_one({"machine_id": machine.machine_id})
    if existing_machine:
        raise HTTPException(
            status_code=400,
            detail="Machine ID already exists"
        )
    
    machine_dict = machine.dict()
    machine_dict["created_at"] = datetime.utcnow()
    machine_dict["updated_at"] = datetime.utcnow()
    
    result = await db.machines.insert_one(machine_dict)
    
    # Retrieve the created machine
    created_machine = await db.machines.find_one({"_id": result.inserted_id})
    created_machine["_id"] = str(created_machine["_id"])
    
    return Machine(**created_machine)

@router.get("/", response_model=List[Machine])
async def get_all_machines(
    status: Optional[MachineStatus] = None,
    location: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Get all machines"""
    db = await get_database()
    
    filter_dict = {}
    if status:
        filter_dict["status"] = status
    if location:
        filter_dict["location"] = {"$regex": location, "$options": "i"}
    
    machines = []
    async for machine in db.machines.find(filter_dict).sort("created_at", -1):
        machine["_id"] = str(machine["_id"])
        machines.append(Machine(**machine))
    
    return machines

@router.get("/{machine_id}", response_model=Machine)
async def get_machine_by_id(
    machine_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get machine by ID"""
    db = await get_database()
    
    if not ObjectId.is_valid(machine_id):
        raise HTTPException(status_code=400, detail="Invalid machine ID")
    
    machine = await db.machines.find_one({"_id": ObjectId(machine_id)})
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    machine["_id"] = str(machine["_id"])
    return Machine(**machine)

@router.get("/machine-id/{machine_id}")
async def get_machine_by_machine_id(
    machine_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get machine by machine_id"""
    db = await get_database()
    
    machine = await db.machines.find_one({"machine_id": machine_id})
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    machine["_id"] = str(machine["_id"])
    return Machine(**machine)

@router.put("/{machine_id}", response_model=Machine)
async def update_machine(
    machine_id: str,
    machine_update: MachineUpdate,
    current_user: User = Depends(check_user_role([UserRole.ADMIN, UserRole.MAINTENANCE]))
):
    """Update machine"""
    db = await get_database()
    
    if not ObjectId.is_valid(machine_id):
        raise HTTPException(status_code=400, detail="Invalid machine ID")
    
    # Check if machine exists
    existing_machine = await db.machines.find_one({"_id": ObjectId(machine_id)})
    if not existing_machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Prepare update data
    update_data = {k: v for k, v in machine_update.dict().items() if v is not None}
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        
        await db.machines.update_one(
            {"_id": ObjectId(machine_id)},
            {"$set": update_data}
        )
    
    # Return updated machine
    updated_machine = await db.machines.find_one({"_id": ObjectId(machine_id)})
    updated_machine["_id"] = str(updated_machine["_id"])
    return Machine(**updated_machine)

@router.delete("/{machine_id}")
async def delete_machine(
    machine_id: str,
    current_user: User = Depends(check_user_role([UserRole.ADMIN]))
):
    """Delete machine (Admin only)"""
    db = await get_database()
    
    if not ObjectId.is_valid(machine_id):
        raise HTTPException(status_code=400, detail="Invalid machine ID")
    
    # Check if there are open issues for this machine
    open_issues = await db.issues.count_documents({
        "machine_id": {"$in": [machine_id, existing_machine.get("machine_id", "")]},
        "status": {"$nin": ["resolved", "closed"]}
    })
    
    # Get machine info first
    existing_machine = await db.machines.find_one({"_id": ObjectId(machine_id)})
    if not existing_machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Check for open issues using both MongoDB ID and machine_id
    open_issues = await db.issues.count_documents({
        "$or": [
            {"machine_id": machine_id},
            {"machine_id": existing_machine.get("machine_id", "")}
        ],
        "status": {"$nin": ["resolved", "closed"]}
    })
    
    if open_issues > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete machine with open issues. Please resolve all issues first."
        )
    
    result = await db.machines.delete_one({"_id": ObjectId(machine_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    return {"message": "Machine deleted successfully"}

@router.get("/location/{location}", response_model=List[Machine])
async def get_machines_by_location(
    location: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get machines by location"""
    db = await get_database()
    
    machines = []
    async for machine in db.machines.find({"location": {"$regex": location, "$options": "i"}}):
        machine["_id"] = str(machine["_id"])
        machines.append(Machine(**machine))
    
    return machines

@router.get("/stats/summary")
async def get_machine_stats(
    current_user: User = Depends(check_user_role([UserRole.ADMIN, UserRole.SAFETY_OFFICER]))
):
    """Get machine statistics"""
    db = await get_database()
    
    # Count machines by status
    stats = {}
    for status in MachineStatus:
        count = await db.machines.count_documents({"status": status})
        stats[f"{status}_count"] = count
    
    # Total machines
    stats["total_machines"] = await db.machines.count_documents({})
    
    # Machines needing maintenance (out of order or scheduled maintenance)
    stats["needs_attention"] = await db.machines.count_documents({
        "status": {"$in": ["maintenance", "out_of_order"]}
    })
    
    return stats

@router.put("/{machine_id}/status")
async def update_machine_status(
    machine_id: str,
    status: MachineStatus,
    current_user: User = Depends(check_user_role([UserRole.ADMIN, UserRole.MAINTENANCE]))
):
    """Update machine status"""
    db = await get_database()
    
    if not ObjectId.is_valid(machine_id):
        raise HTTPException(status_code=400, detail="Invalid machine ID")
    
    # Check if machine exists
    machine = await db.machines.find_one({"_id": ObjectId(machine_id)})
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Update status
    update_data = {
        "status": status,
        "updated_at": datetime.utcnow()
    }
    
    # If setting to operational, update last_maintenance
    if status == MachineStatus.operational:
        update_data["last_maintenance"] = datetime.utcnow()
    
    await db.machines.update_one(
        {"_id": ObjectId(machine_id)},
        {"$set": update_data}
    )
    
    # Return updated machine
    updated_machine = await db.machines.find_one({"_id": ObjectId(machine_id)})
    updated_machine["_id"] = str(updated_machine["_id"])
    return Machine(**updated_machine)
