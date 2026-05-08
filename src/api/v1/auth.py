from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from src.setup.database import get_db
from src.setup.dependencies import CurrentUser
from src.setup.local_auth import create_access_token, verify_password, get_password_hash, decode_access_token
from src.models.core import FacultyProfile
from src.schema.core import FacultyProfileCreate, FacultyProfileUpdate
from src.crud.core import get_faculty_by_email
from src.setup.email_utils import send_verification_email
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    token: str
    profile: dict

@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await get_faculty_by_email(db, data.email)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified. Please check your inbox.")
    
    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "appraisal_role": user.appraisal_role,
        "department": user.department,
        "school": user.school
    })
    
    return {
        "token": token,
        "profile": {
            "email": user.email,
            "full_name": user.full_name,
            "role": user.appraisal_role, 
            "appraisal_role": user.appraisal_role,
            "department": user.department,
            "school": user.school,
            "employee_id": user.employee_id,
            "designation": user.designation,
            "phone": user.phone,
            "profile_picture_url": user.avatar
        }
    }

@router.post("/register")
async def register(data: FacultyProfileCreate, db: AsyncSession = Depends(get_db)):
    existing = await get_faculty_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = FacultyProfile(
        email=data.email,
        password_hash=get_password_hash(data.password),
        full_name=data.full_name,
        appraisal_role=data.appraisal_role,
        school=data.school,
        department=data.department,
        designation=data.designation,
        employee_id=data.employee_id,
        phone=data.phone,
        qualification=data.qualification,
        teaching_experience=data.teaching_experience,
        is_verified=False
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Send verification email
    verify_token = create_access_token({"sub": str(new_user.id), "email": new_user.email})
    await send_verification_email(new_user.email, verify_token)
    
    return {
        "message": "Registration successful. Please check your email to verify your account.",
        "email": new_user.email
    }

@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    frontend_login_url = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/") + "/login"
    try:
        logger.info("Email verification attempt started.")
        payload = decode_access_token(token)
        email = payload.get("email")
        if not email:
            logger.warning("Email verification failed: No email in token.")
            return RedirectResponse(url=f"{frontend_login_url}?error=invalid_token")
        
        user = await get_faculty_by_email(db, email)
        if not user:
            logger.warning(f"Email verification failed: User {email} not found.")
            return RedirectResponse(url=f"{frontend_login_url}?error=user_not_found")
        
        if not user.is_verified:
            user.is_verified = True
            await db.commit()
            logger.info(f"Email verification successful for {email}.")
        else:
            logger.info(f"Email already verified for {email}.")
            
        return RedirectResponse(url=f"{frontend_login_url}?verified=true")
    except Exception as e:
        logger.error(f"Email verification exception: {str(e)}")
        return RedirectResponse(url=f"{frontend_login_url}?error=verification_failed")

@router.get("/me")
async def get_me(current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    user = await get_faculty_by_email(db, current_user.email)
    return {
        "email": user.email,
        "full_name": user.full_name,
        "role": user.appraisal_role,
        "appraisal_role": user.appraisal_role,
        "department": user.department,
        "school": user.school,
        "employee_id": user.employee_id,
        "designation": user.designation,
        "phone": user.phone,
        "profile_picture_url": user.avatar
    }

@router.put("/me")
async def update_me(data: FacultyProfileUpdate, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    user = await get_faculty_by_email(db, current_user.email)
    if data.full_name: user.full_name = data.full_name
    if data.department: user.department = data.department
    if data.school: user.school = data.school
    if data.designation: user.designation = data.designation
    if data.phone: user.phone = data.phone
    if data.avatar: user.avatar = data.avatar 
    
    await db.commit()
    await db.refresh(user)
    return {
        "email": user.email,
        "full_name": user.full_name,
        "role": user.appraisal_role,
        "appraisal_role": user.appraisal_role,
        "department": user.department,
        "school": user.school,
        "employee_id": user.employee_id,
        "designation": user.designation,
        "phone": user.phone,
        "profile_picture_url": user.avatar
    }

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.post("/change-password")
async def change_password(data: ChangePasswordRequest, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    user = await get_faculty_by_email(db, current_user.email)
    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    user.password_hash = get_password_hash(data.new_password)
    await db.commit()
    return {"message": "Password changed successfully"}

@router.post("/forgot-password")
async def forgot_password(data: dict):
    return {"message": "Reset link sent"}

@router.post("/reset-password")
async def reset_password(data: dict):
    return {"message": "Password reset successful"}
