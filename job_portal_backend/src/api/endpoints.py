from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional

from .schemas import (
    UserCreate, UserUpdate, UserPublic, Role,
    ProfilePublic, ProfileUpdate,
    JobCreate, JobUpdate, JobPublic,
    ApplicationCreate, ApplicationUpdate, ApplicationPublic
)

## Dummy dependencies and user role checks for demonstration. Replace with real authentication/authorization logic in production.
def get_current_user():
    """
    Dummy dependency to simulate user retrieval. Replace with session/auth token logic.
    """
    class User:
        id = 1
        email = "admin@example.com"
        full_name = "Admin"
        role = Role.admin
    return User()

def require_role(required_role: Role):
    def role_checker(current_user=Depends(get_current_user)):
        if current_user.role != required_role and current_user.role != Role.admin:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

router = APIRouter()

# ------------------- Users -------------------

@router.post("/users", response_model=UserPublic, tags=["Users"], summary="Register user")
def create_user(user: UserCreate):
    """
    Register a new user (job seeker or employer).
    """
    # Logic to create user goes here.
    pass

@router.get("/users/me", response_model=UserPublic, tags=["Users"], summary="Current user info")
def get_me(current_user=Depends(get_current_user)):
    """
    Get profile info for currently logged-in user.
    """
    return current_user

@router.get("/users/{user_id}", response_model=UserPublic, tags=["Users"], summary="Get user by ID")
def get_user(user_id: int, current_user=Depends(require_role(Role.admin))):
    """
    Retrieve a user account by id. Only accessible by admins.
    """
    pass

@router.patch("/users/{user_id}", response_model=UserPublic, tags=["Users"], summary="Update user")
def update_user(user_id: int, user: UserUpdate, current_user=Depends(get_current_user)):
    """
    Update account info for the given user. Must be self or admin.
    """
    pass

@router.delete("/users/{user_id}", status_code=204, tags=["Users"], summary="Delete user")
def delete_user(user_id: int, current_user=Depends(require_role(Role.admin))):
    """
    Delete a user account. Only accessible by admins.
    """
    pass

# --------------- Profile ---------------------

@router.get("/profiles/{user_id}", response_model=ProfilePublic, tags=["Profiles"], summary="Get user profile")
def get_profile(user_id: int):
    """
    Retrieve the profile for a given user (public, read-only).
    """
    pass

@router.put("/profiles/me", response_model=ProfilePublic, tags=["Profiles"], summary="Update my profile")
def update_profile(profile: ProfileUpdate, current_user=Depends(require_role(Role.job_seeker))):
    """
    Update the authenticated user's profile.
    """
    pass

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
