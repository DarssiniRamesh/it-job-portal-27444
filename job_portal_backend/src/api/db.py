import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import StaticPool

from .models import Base

# Get DB URL from env or default to SQLite (for local/dev)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./itjobportal_dev.db")

# Configure engine for SQLite in-memory if no DB url is provided; otherwise, prefer user config.
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# PUBLIC_INTERFACE
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


# PUBLIC_INTERFACE
def get_db():
    """Yield a db session, closing after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# PUBLIC_INTERFACE
def init_db():
    """
    Initialize the database tables.
    This should be called at startup or via a migration/init script.
    """
    try:
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as e:
        print(f"Failed to initialize the database: {str(e)}")
        raise
