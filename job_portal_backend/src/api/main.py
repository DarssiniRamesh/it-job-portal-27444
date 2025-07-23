from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .endpoints import router as api_router
from .db import init_db, get_db
from . import models
from .auth import create_access_token, get_password_hash, authenticate_user
from .models import User
from .schemas import UserCreate, UserPublic

openapi_tags = [
    {"name": "Users", "description": "User registration, profile, and admin management."},
    {"name": "Jobs", "description": "Manage job postings (create, search, update, delete)."},
    {"name": "Applications", "description": "Job applications workflow."},
    {"name": "Profiles", "description": "Profile management for job seekers."}
]

app = FastAPI(
    title="IT Job Portal Backend",
    description="Backend API for IT Job Portal - provides Job, User, Profile, and Application management.",
    version="0.1.0",
    openapi_tags=openapi_tags
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize tables at startup if not already present
@app.on_event("startup")
def _create_tables_if_needed():
    init_db()

from fastapi import APIRouter

auth_router = APIRouter(tags=["Auth"])

@auth_router.post("/auth/register", response_model=UserPublic, summary="Register a new user")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user (job seeker or employer/employer admin).
    """
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered.")
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        hashed_password=get_password_hash(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserPublic(
        id=db_user.id,
        email=db_user.email,
        full_name=db_user.full_name,
        role=db_user.role.value if hasattr(db_user.role, "value") else db_user.role,
    )

@auth_router.post("/auth/login", summary="User login and JWT issuance")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login endpoint. Accepts OAuth2 password grant, returns access token.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

# Mount REST API routes and auth router
app.include_router(auth_router)
app.include_router(api_router)

@app.get("/", tags=["Users"])
def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}
