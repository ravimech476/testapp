from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    SAFETY_OFFICER = "safety_officer"
    MAINTENANCE = "maintenance"
    EMPLOYEE = "employee"

class IssueStatus(str, Enum):
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class IssuePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MachineStatus(str, Enum):
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    OUT_OF_ORDER = "out_of_order"

# User Models
class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    id: str = Field(alias="_id")
    hashed_password: str
    created_at: datetime
    updated_at: datetime

class User(UserBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

# Machine Models
class MachineBase(BaseModel):
    name: str
    machine_id: str
    description: Optional[str] = None
    location: str
    status: MachineStatus = MachineStatus.OPERATIONAL
    last_maintenance: Optional[datetime] = None

class MachineCreate(MachineBase):
    pass

class MachineUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    status: Optional[MachineStatus] = None
    last_maintenance: Optional[datetime] = None

class Machine(MachineBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

# Issue Models
class IssueBase(BaseModel):
    title: str
    description: str
    machine_id: str
    priority: IssuePriority = IssuePriority.MEDIUM
    status: IssueStatus = IssueStatus.OPEN

class IssueCreate(IssueBase):
    pass

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[IssuePriority] = None
    status: Optional[IssueStatus] = None
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None

class Issue(IssueBase):
    id: str = Field(alias="_id")
    reported_by: str
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
    photos: List[str] = []
    resolution_photos: List[str] = []
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

# Authentication Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str
