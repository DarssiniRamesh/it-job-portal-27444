from fastapi import Depends
from .db import get_db
from .models import User
from .auth import get_current_user

# Re-export for convenience, may add more as needed.
# PUBLIC_INTERFACE
def get_db_session():
    """Yield a DB session for dependency injection."""
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

# PUBLIC_INTERFACE
def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Raise if user is not active (for future use)."""
    return current_user
