from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.setup.database import get_db
from src.setup.dependencies import CurrentUser
from src.setup.local_auth import create_access_token, verify_password, get_password_hash
from src.models.core import FacultyProfile
from src.schema.core import FacultyProfileCreate, FacultyProfileUpdate
from src.crud.core import get_faculty_by_email
from pydantic import BaseModel, EmailStr
from typing import Optional

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
    
    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "appraisal_role": user.appraisal_role,
        "department": user.department,
        "school": user.school,
        "division": user.division,
        "form_family": user.form_family
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
            "division": user.division,
            "form_family": user.form_family,
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
    
    # Map school to form_family
    school_map = {
        "SoCSEA": "standard", "SoBB": "standard", "SoCE": "standard", 
        "SoEMR": "standard", "SoC": "standard", "CISR": "standard",
        "SoMCS": "media",
        "CioD": "design", "SoAA": "design"
    }
    assigned_family = school_map.get(data.school, "standard")
    
    new_user = FacultyProfile(
        email=data.email,
        password_hash=get_password_hash(data.password),
        full_name=data.full_name,
        appraisal_role=data.appraisal_role,
        school=data.school,
        department=data.department,
        division=data.division,
        form_family=assigned_family,
        designation=data.designation,
        employee_id=data.employee_id,
        phone=data.phone,
        qualification=data.qualification,
        teaching_experience=data.teaching_experience
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return {
        "email": new_user.email,
        "full_name": new_user.full_name,
        "role": new_user.appraisal_role,
        "appraisal_role": new_user.appraisal_role,
        "department": new_user.department,
        "school": new_user.school,
        "division": new_user.division,
        "form_family": new_user.form_family,
        "employee_id": new_user.employee_id,
        "designation": new_user.designation,
        "phone": new_user.phone,
        "profile_picture_url": new_user.avatar
    }

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
        "division": user.division,
        "form_family": user.form_family,
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
    if data.division: user.division = data.division
    if data.form_family: user.form_family = data.form_family
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
        "division": user.division,
        "form_family": user.form_family,
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
