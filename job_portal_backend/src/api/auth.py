import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from .db import get_db
from .models import User, RoleEnum
from .schemas import Role

from sqlalchemy.orm import Session

# Configurable settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "devsecret_jwt_change_this")  # In prod, set via env variable!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# PUBLIC_INTERFACE
def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user and return user object if valid, else None."""
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

# PUBLIC_INTERFACE
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT token and embed user info/claims."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# PUBLIC_INTERFACE
def get_current_user(request: Request, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    """
    Decode and return the current user based on the JWT token.
    Throws 401 if the token is invalid/expired or user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# PUBLIC_INTERFACE
def require_role(required_role: Role):
    """
    Dependency for strict role (job_seeker, employer, admin).
    Admin has full access.
    """
    def role_checker(
        current_user: User = Depends(get_current_user)
    ):
        user_role = (
            current_user.role.value if isinstance(current_user.role, RoleEnum) else current_user.role
        )
        req_role = required_role.value if isinstance(required_role, RoleEnum) else required_role
        if user_role != req_role and user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions for role: {required_role}",
            )
        return current_user
    return role_checker

# PUBLIC_INTERFACE
def require_any_role(*roles: Role):
    """
    Dependency for OR-role access (e.g., job_seeker or employer).
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        user_role = (
            current_user.role.value if isinstance(current_user.role, RoleEnum) else current_user.role
        )
        allowed = {r.value if isinstance(r, RoleEnum) else r for r in roles}
        if user_role in allowed or user_role == "admin":
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions.",
        )
    return role_checker

# PUBLIC_INTERFACE
def require_self_or_admin(entity_user_id_param: int):
    """
    Dependency to allow the user themselves or admin to act.
    """
    def checker(
        current_user: User = Depends(get_current_user)
    ):
        user_role = (
            current_user.role.value if isinstance(current_user.role, RoleEnum) else current_user.role
        )
        if current_user.id == entity_user_id_param or user_role == "admin":
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized for this user.",
        )
    return checker
