from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .endpoints import router as api_router

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

# Mount REST API routes
app.include_router(api_router)

@app.get("/", tags=["Users"])
def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}
