from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from .schemas import (
    UserCreate, UserUpdate, UserPublic, Role,
    ProfilePublic, ProfileUpdate,
    JobCreate, JobUpdate, JobPublic,
    ApplicationCreate, ApplicationUpdate, ApplicationPublic
)
from .models import User, Profile, RoleEnum
from .db import get_db
from .auth import (
    require_role, get_current_user, get_password_hash
)

router = APIRouter()

# ------------------- Users -------------------

# PUBLIC_INTERFACE
@router.post("/users", response_model=UserPublic, tags=["Users"], summary="Register user")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user (job seeker or employer).
    """
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered.")
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        hashed_password=get_password_hash(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # Create empty profile for the user, job seekers only
    if db_user.role == RoleEnum.job_seeker:
        profile = Profile(user_id=db_user.id)
        db.add(profile)
        db.commit()
    return UserPublic(
        id=db_user.id,
        email=db_user.email,
        full_name=db_user.full_name,
        role=db_user.role.value if hasattr(db_user.role, "value") else db_user.role,
    )

# PUBLIC_INTERFACE
@router.get("/users/me", response_model=UserPublic, tags=["Users"], summary="Current user info")
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get profile info for currently logged-in user.
    """
    return UserPublic(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.value if hasattr(current_user.role, "value") else current_user.role,
    )

# PUBLIC_INTERFACE
@router.get("/users/{user_id}", response_model=UserPublic, tags=["Users"], summary="Get user by ID")
def get_user(user_id: int, current_user: User = Depends(require_role(Role.admin)), db: Session = Depends(get_db)):
    """
    Retrieve a user account by id. Only accessible by admins.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return UserPublic(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value if hasattr(user.role, "value") else user.role,
    )

# PUBLIC_INTERFACE
@router.patch("/users/{user_id}", response_model=UserPublic, tags=["Users"], summary="Update user")
def update_user(
    user_id: int,
    user: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update account info for the given user. Must be self or admin.
    """
    if not (current_user.id == user_id or (current_user.role.value if hasattr(current_user.role, 'value') else current_user.role) == "admin"):
        raise HTTPException(status_code=403, detail="Not authorized to update this user.")
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.full_name is not None:
        db_user.full_name = user.full_name
    if user.password is not None:
        db_user.hashed_password = get_password_hash(user.password)
    db.commit()
    db.refresh(db_user)
    return UserPublic(
        id=db_user.id,
        email=db_user.email,
        full_name=db_user.full_name,
        role=db_user.role.value if hasattr(db_user.role, "value") else db_user.role,
    )

# PUBLIC_INTERFACE
@router.delete("/users/{user_id}", status_code=204, tags=["Users"], summary="Delete user")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_role(Role.admin)),
    db: Session = Depends(get_db)
):
    """
    Delete a user account. Only accessible by admins.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    db.delete(user)
    db.commit()
    return

# --------------- Profile ---------------------

# PUBLIC_INTERFACE
@router.get("/profiles/{user_id}", response_model=ProfilePublic, tags=["Profiles"], summary="Get user profile")
def get_profile(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve the profile for a given user (public, read-only).
    """
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found for this user.")
    return ProfilePublic(
        id=profile.id,
        user_id=profile.user_id,
        headline=profile.headline,
        skills=profile.skills_list,
        experience=profile.experience,
        education=profile.education,
    )

# PUBLIC_INTERFACE
@router.put("/profiles/me", response_model=ProfilePublic, tags=["Profiles"], summary="Update my profile")
def update_profile(
    profile: ProfileUpdate,
    current_user: User = Depends(require_role(Role.job_seeker)),
    db: Session = Depends(get_db)
):
    """
    Update the authenticated user's profile.
    """
    db_profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not db_profile:
        db_profile = Profile(user_id=current_user.id)
        db.add(db_profile)
    if profile.headline is not None:
        db_profile.headline = profile.headline
    if profile.skills is not None:
        db_profile.skills_list = profile.skills
    if profile.experience is not None:
        db_profile.experience = profile.experience
    if profile.education is not None:
        db_profile.education = profile.education
    db.commit()
    db.refresh(db_profile)
    return ProfilePublic(
        id=db_profile.id,
        user_id=db_profile.user_id,
        headline=db_profile.headline,
        skills=db_profile.skills_list,
        experience=db_profile.experience,
        education=db_profile.education,
    )

# --------------- Jobs ------------------------

@router.post("/jobs", response_model=JobPublic, tags=["Jobs"], summary="Create job posting")
def create_job(job: JobCreate, current_user=Depends(require_role(Role.employer))):
    """
    Employer creates a new job posting.
    """
    pass

@router.get("/jobs", response_model=List[JobPublic], tags=["Jobs"], summary="List/search jobs")
def list_jobs(
    q: Optional[str] = Query(None, description="Free-text search"),
    location: Optional[str] = None,
    remote: Optional[bool] = None,
    tags: Optional[List[str]] = Query(None, description="Filter by skills/tags"),
    skip: int = 0,
    limit: int = 20,
):
    """
    Search and filter job postings.
    """
    pass

@router.get("/jobs/{job_id}", response_model=JobPublic, tags=["Jobs"], summary="Get job by ID")
def get_job(job_id: int):
    """
    Get job details.
    """
    pass

@router.patch("/jobs/{job_id}", response_model=JobPublic, tags=["Jobs"], summary="Update job posting")
def update_job(job_id: int, job: JobUpdate, current_user=Depends(require_role(Role.employer))):
    """
    Employer updates a job posting.
    """
    pass

@router.delete("/jobs/{job_id}", status_code=204, tags=["Jobs"], summary="Delete job posting")
def delete_job(job_id: int, current_user=Depends(require_role(Role.employer))):
    """
    Employer deletes a job posting.
    """
    pass

# ------------- Applications -----------------

@router.post("/applications", response_model=ApplicationPublic, tags=["Applications"], summary="Apply to job")
def create_application(app: ApplicationCreate, current_user=Depends(require_role(Role.job_seeker))):
    """
    Submit a job application as a job seeker.
    """
    pass

@router.get("/applications/{app_id}", response_model=ApplicationPublic, tags=["Applications"], summary="Get application")
def get_application(app_id: int, current_user=Depends(get_current_user)):
    """
    Get single application. Job seekers must be owner, employers must own job.
    """
    pass

@router.get("/applications", response_model=List[ApplicationPublic], tags=["Applications"], summary="List my applications")
def list_my_applications(current_user=Depends(get_current_user)):
    """
    List all job applications submitted by the current job seeker.
    """
    pass

@router.patch("/applications/{app_id}", response_model=ApplicationPublic, tags=["Applications"], summary="Manage application")
def update_application(
    app_id: int, 
    update: ApplicationUpdate, 
    current_user=Depends(require_role(Role.employer)),
):
    """
    Update application status/notes (employer action).
    """
    pass
