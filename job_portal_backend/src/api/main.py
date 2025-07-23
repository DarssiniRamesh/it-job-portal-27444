from fastapi import FastAPI, Request, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .endpoints import router as api_router
from .db import init_db, get_db
from . import models
from .auth import create_access_token, get_password_hash, authenticate_user
from .models import User
from .schemas import UserCreate, UserPublic

# Import dashboard endpoints
from . import dashboard

openapi_tags = [
    {"name": "Users", "description": "User registration, profile, and admin management."},
    {"name": "Jobs", "description": "Manage job postings (create, search, update, delete)."},
    {"name": "Applications", "description": "Job applications workflow."},
    {"name": "Profiles", "description": "Profile management for job seekers."},
    {"name": "Dashboard", "description": "Aggregate dashboard data for employers and job seekers."}
]

app = FastAPI(
    title="IT Job Portal Backend",
    description="Backend API for IT Job Portal - provides Job, User, Profile, and Application management.",
    version="0.1.0",
    openapi_tags=openapi_tags
)

# --- Robust, production-friendly CORS configuration ---
# (For production: change allow_origins to specific domains as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Security Middleware: Add basic security headers ---
class SecureHeadersMiddleware(BaseHTTPMiddleware):
    """Add common security headers to all responses."""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Permissions-Policy"] = "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()"
        return response

app.add_middleware(SecureHeadersMiddleware)

# --- Robust Exception Handlers ---
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTPException handler with structured response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "type": "HTTPException"},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all for uncaught exceptions with logging."""
    # Log exception here if using logging system
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "An unexpected error occurred.", "type": "InternalServerError"},
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
app.include_router(dashboard.router)

@app.get("/", tags=["Users"])
def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}

