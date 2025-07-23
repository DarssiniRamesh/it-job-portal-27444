from sqlalchemy import (
    Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Enum, Text
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()

# Enum types
class RoleEnum(enum.Enum):
    job_seeker = "job_seeker"
    employer = "employer"
    admin = "admin"

class ApplicationStatusEnum(enum.Enum):
    submitted = "submitted"
    viewed = "viewed"
    shortlisted = "shortlisted"
    rejected = "rejected"
    accepted = "accepted"


# Association for list-of-strings (fallback for basic SQLite compatibility)
def _comma_string():
    return ""

def list_to_str(lst):
    return ",".join(lst) if lst else ""

def str_to_list(val):
    if not val or not isinstance(val, str):
        return []
    return [s for s in val.split(",") if s]


# PUBLIC_INTERFACE
class User(Base):
    """User account in the system."""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    hashed_password = Column(String, nullable=False)

    # Relationships
    profile = relationship("Profile", uselist=False, back_populates="user")
    jobs = relationship("Job", back_populates="employer", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")


# PUBLIC_INTERFACE
class Profile(Base):
    """Profile for a user."""
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    headline = Column(String, nullable=True)
    skills = Column(String, nullable=True)    # Stored as comma-separated string for skills
    experience = Column(Text, nullable=True)
    education = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="profile")

    @property
    def skills_list(self):
        return str_to_list(self.skills)

    @skills_list.setter
    def skills_list(self, value):
        self.skills = list_to_str(value)


# PUBLIC_INTERFACE
class Job(Base):
    """Job posting by an employer."""
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(String, nullable=True)  # Comma-separated list
    location = Column(String, nullable=False)
    company = Column(String, nullable=False)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    remote = Column(Boolean, default=False, nullable=False)
    tags = Column(String, nullable=True) # Comma-separated list

    employer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    employer = relationship("User", back_populates="jobs")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")

    @property
    def requirements_list(self):
        return str_to_list(self.requirements)

    @requirements_list.setter
    def requirements_list(self, value):
        self.requirements = list_to_str(value)

    @property
    def tags_list(self):
        return str_to_list(self.tags)

    @tags_list.setter
    def tags_list(self, value):
        self.tags = list_to_str(value)


# PUBLIC_INTERFACE
class Application(Base):
    """Job application."""
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cover_letter = Column(Text, nullable=True)
    status = Column(Enum(ApplicationStatusEnum), default=ApplicationStatusEnum.submitted, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
