from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# PUBLIC_INTERFACE
class Role(str, Enum):
    job_seeker = "job_seeker"
    employer = "employer"
    admin = "admin"

# PUBLIC_INTERFACE
class UserBase(BaseModel):
    """Base fields for a User in the system."""
    email: EmailStr = Field(..., description="User's email address")
    full_name: str = Field(..., description="User's full name")
    role: Role = Field(..., description="Role of the user (job_seeker, employer, admin)")

# PUBLIC_INTERFACE
class UserCreate(UserBase):
    """Fields required for user registration."""
    password: str = Field(..., min_length=6, description="Password for the user")

# PUBLIC_INTERFACE
class UserUpdate(BaseModel):
    """Fields updatable by user."""
    full_name: Optional[str] = Field(None, description="User's full name")
    password: Optional[str] = Field(None, min_length=6, description="New password")

# PUBLIC_INTERFACE
class UserInDB(UserBase):
    """User model representation in DB, with hashed_password."""
    id: int = Field(..., description="Unique user identifier")
    hashed_password: str = Field(..., description="Hashed user password")

# PUBLIC_INTERFACE
class UserPublic(UserBase):
    """User information returned to clients."""
    id: int

# PUBLIC_INTERFACE
class ProfileBase(BaseModel):
    """Base fields for user profile."""
    headline: Optional[str] = Field(None, description="Profile headline")
    skills: Optional[List[str]] = Field(None, description="List of skills")
    experience: Optional[str] = Field(None, description="Work experience summary")
    education: Optional[str] = Field(None, description="Education background")

# PUBLIC_INTERFACE
class ProfileUpdate(ProfileBase):
    """Fields updatable in profile."""
    pass

# PUBLIC_INTERFACE
class ProfileInDB(ProfileBase):
    """DB representation of a profile."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

# PUBLIC_INTERFACE
class ProfilePublic(ProfileBase):
    """Profile returned to clients."""
    id: int
    user_id: int

# PUBLIC_INTERFACE
class JobBase(BaseModel):
    """Base job posting information."""
    title: str = Field(..., description="Job title")
    description: str = Field(..., description="Job description")
    requirements: Optional[List[str]] = Field(None, description="List of requirements")
    location: str = Field(..., description="Job location")
    company: str = Field(..., description="Company name")
    salary_min: Optional[float] = Field(None, description="Minimum salary")
    salary_max: Optional[float] = Field(None, description="Maximum salary")
    remote: bool = Field(False, description="Remote job")
    tags: Optional[List[str]] = Field(None, description="Tags for this job (e.g. Python, IT)")

# PUBLIC_INTERFACE
class JobCreate(JobBase):
    pass

# PUBLIC_INTERFACE
class JobUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    requirements: Optional[List[str]]
    location: Optional[str]
    company: Optional[str]
    salary_min: Optional[float]
    salary_max: Optional[float]
    remote: Optional[bool]
    tags: Optional[List[str]]

# PUBLIC_INTERFACE
class JobInDB(JobBase):
    id: int
    employer_id: int
    created_at: datetime
    updated_at: datetime

# PUBLIC_INTERFACE
class JobPublic(JobBase):
    id: int
    employer_id: int

# PUBLIC_INTERFACE
class ApplicationStatus(str, Enum):
    submitted = "submitted"
    viewed = "viewed"
    shortlisted = "shortlisted"
    rejected = "rejected"
    accepted = "accepted"

# PUBLIC_INTERFACE
class ApplicationBase(BaseModel):
    job_id: int = Field(..., description="Job reference id")
    user_id: int = Field(..., description="Job seeker user id")
    cover_letter: Optional[str] = Field(None, description="Cover letter from job seeker")

# PUBLIC_INTERFACE
class ApplicationCreate(ApplicationBase):
    pass

# PUBLIC_INTERFACE
class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = Field(None, description="Status set by Employer/Admin")
    notes: Optional[str] = Field(None, description="Application notes")

# PUBLIC_INTERFACE
class ApplicationInDB(ApplicationBase):
    id: int
    status: ApplicationStatus
    created_at: datetime
    updated_at: datetime

# PUBLIC_INTERFACE
class ApplicationPublic(ApplicationBase):
    id: int
    status: ApplicationStatus
