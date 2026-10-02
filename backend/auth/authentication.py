import uuid
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.database.database import get_db, SessionLocal
from backend.database.models import User
from .password import hash_password, verify_password
from .session import create_access_token, decode_access_token
from .models import TokenData

security = HTTPBearer(auto_error=False)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email.lower()).first()

def create_user(db: Session, email: str, password: str, full_name: str, role: str = "customer", user_id: Optional[str] = None) -> User:
    if not user_id:
        if role == "customer":
            user_id = f"CUS-{uuid.uuid4().hex[:6].upper()}"
        else:
            user_id = f"USR-{uuid.uuid4().hex[:6].upper()}"
    hashed_pwd = hash_password(password)
    new_user = User(
        id=user_id,
        email=email.lower(),
        password_hash=hashed_pwd,
        full_name=full_name,
        role=role,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    if not credentials:
        return None
    token_data = decode_access_token(credentials.credentials)
    if not token_data or not token_data.email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user_by_email(db, token_data.email)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    return user

def seed_default_users():
    """Seeds default enterprise users if they do not already exist."""
    db = SessionLocal()
    try:
        defaults = [
            ("USR-ADMIN01", "admin@support.ai", "admin123", "System Administrator", "admin"),
            ("USR-AGENT01", "agent@support.ai", "agent123", "Lead Support Specialist", "agent"),
            ("CUS-8821", "customer@support.ai", "customer123", "Rajesh Kumar", "customer"),
            ("CUS-9410", "priya.sharma@example.com", "customer123", "Priya Sharma", "customer"),
            ("CUS-7712", "anand.v@example.com", "customer123", "Anand Venkatesh", "customer")
        ]
        for uid, email, pwd, name, role in defaults:
            existing = get_user_by_email(db, email)
            if not existing:
                create_user(db, email, pwd, name, role, user_id=uid)
            elif uid and existing.id != uid:
                existing.id = uid
                db.commit()
    finally:
        db.close()
