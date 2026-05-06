from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, EmailStr
from typing import Dict
from src.setup.database import get_db
from src.models.Part_B.faculty import Faculty
from src.setup.local_auth import verify_password, get_password_hash, create_access_token
from src.setup.email_utils import send_verification_email
import os
import secrets

from src.setup.dependencies import CurrentUser

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Verifies the user's email using the provided token.
    """
    query = select(Faculty).where(Faculty.verification_token == token)
    result = await db.execute(query)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token.")
        
    user.is_verified = True
    user.verification_token = None
    await db.commit()
    
    return {"message": "Email verified successfully. You can now log in."}

@router.get("/session", response_model=Dict)
async def get_session(current_user: CurrentUser):
    """
    Returns the current session details if the token is valid.
    Used by frontend to verify login status.
    """
    return {
        "id": current_user.id,
        "roles": current_user.roles,
        "department": current_user.department,
        "school_id": current_user.school_id
    }

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    department: str
    role: str = "faculty"

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user and send a verification email.
    """
    if os.getenv("USE_LOCAL_AUTH", "false").lower() != "true":
        raise HTTPException(status_code=400, detail="Local authentication is not enabled.")

    query = select(Faculty).where(Faculty.email == user_in.email)
    result = await db.execute(query)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered.")
    
    v_token = secrets.token_urlsafe(32)
    new_user = Faculty(
        email=user_in.email,
        name=user_in.name,
        department=user_in.department,
        role=user_in.role,
        hashed_password=get_password_hash(user_in.password),
        is_verified=False,
        verification_token=v_token
    )
    
    db.add(new_user)
    await db.commit()
    
    # Send email
    await send_verification_email(new_user.email, v_token)
    
    return {"message": "User registered. Please check your email to verify your account."}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Login endpoint. Only allows verified users.
    """
    if os.getenv("USE_LOCAL_AUTH", "false").lower() != "true":
        raise HTTPException(status_code=400, detail="Local authentication is not enabled.")
        
    query = select(Faculty).where(Faculty.email == form_data.username)
    result = await db.execute(query)
    user = result.scalars().first()
    
    if not user or not user.hashed_password or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not verified. Please check your inbox.")
        
    access_token = create_access_token(data={
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "department": user.department,
        "school_id": str(user.school_id) if user.school_id else None
    })
    
    return {"access_token": access_token, "token_type": "bearer"}
