from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct
from src.setup.database import get_db
from src.setup.dependencies import CurrentUser
from src.models.core import FacultyProfile, Declaration, AppraisalReview
from src.models.non_teaching import NonTeachingAppraisal
from src.setup.local_auth import get_password_hash
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from pathlib import Path
from dotenv import dotenv_values, set_key
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])

# Keys the admin UI is allowed to read and write.
# DATABASE_URL, JWT_SECRET_KEY, and SUPABASE_* are intentionally excluded.
EDITABLE_ENV_KEYS = frozenset({
    "MAIL_USERNAME", "MAIL_PASSWORD", "MAIL_FROM", "MAIL_PORT",
    "MAIL_SERVER", "MAIL_TLS", "MAIL_SSL",
    "APP_URL", "FRONTEND_URL", "ALLOW_MOCK_USER",
    "USE_LOCAL_STORAGE", "GCP_STORAGE_BUCKET",
})

VALID_ROLES = frozenset({
    "faculty", "non_teaching_staff", "staff", "hod", "reporting_officer",
    "section_head", "director", "center_head", "dean", "registrar", "vc", "admin",
})


def _check_admin(current_user):
    if "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Admin role required")


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

@router.get("/stats")
async def get_stats(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    academic_year: Optional[str] = Query(None),
):
    _check_admin(current_user)

    # Collect distinct years from both teaching and non-teaching tables
    t_years = await db.execute(
        select(distinct(Declaration.academic_year)).order_by(Declaration.academic_year.desc())
    )
    nt_years = await db.execute(
        select(distinct(NonTeachingAppraisal.academic_year)).order_by(NonTeachingAppraisal.academic_year.desc())
    )
    available_years = sorted(
        set([r[0] for r in t_years.all()] + [r[0] for r in nt_years.all()]),
        reverse=True,
    )

    if not academic_year:
        academic_year = available_years[0] if available_years else None

    # Registered users by role and school
    role_res = await db.execute(
        select(FacultyProfile.appraisal_role, func.count(FacultyProfile.id))
        .group_by(FacultyProfile.appraisal_role)
    )
    by_role = {row[0]: row[1] for row in role_res.all()}

    school_res = await db.execute(
        select(FacultyProfile.school, func.count(FacultyProfile.id))
        .group_by(FacultyProfile.school)
    )
    by_school_registered = {row[0]: row[1] for row in school_res.all()}

    teaching_pipeline: dict = {}
    by_school_submitted: dict = {}
    non_teaching_pipeline: dict = {}

    if academic_year:
        # Teaching submission pipeline for the selected year
        pipe_res = await db.execute(
            select(Declaration.status, func.count(Declaration.id))
            .where(Declaration.academic_year == academic_year)
            .group_by(Declaration.status)
        )
        teaching_pipeline = {row[0]: row[1] for row in pipe_res.all()}

        # Per-school breakdown for the selected year
        school_sub_res = await db.execute(
            select(FacultyProfile.school, Declaration.status, func.count(Declaration.id))
            .join(Declaration, FacultyProfile.email == Declaration.faculty_email)
            .where(Declaration.academic_year == academic_year)
            .group_by(FacultyProfile.school, Declaration.status)
        )
        for school, status, count in school_sub_res.all():
            by_school_submitted.setdefault(school, {})[status] = count

        # Non-teaching pipeline for the selected year
        nt_pipe_res = await db.execute(
            select(NonTeachingAppraisal.status, func.count(NonTeachingAppraisal.id))
            .where(NonTeachingAppraisal.academic_year == academic_year)
            .group_by(NonTeachingAppraisal.status)
        )
        non_teaching_pipeline = {row[0]: row[1] for row in nt_pipe_res.all()}

    return {
        "academic_year": academic_year,
        "available_years": available_years,
        "total_registered": sum(by_role.values()),
        "by_role": by_role,
        "by_school_registered": by_school_registered,
        "teaching_submission_pipeline": teaching_pipeline,
        "by_school_submitted": by_school_submitted,
        "non_teaching_pipeline": non_teaching_pipeline,
    }


# ---------------------------------------------------------------------------
# Env config
# ---------------------------------------------------------------------------

@router.get("/config")
async def get_config(current_user: CurrentUser):
    _check_admin(current_user)
    env_path = Path(".env")
    if not env_path.exists():
        return {}
    values = dotenv_values(env_path)
    return {k: v for k, v in values.items() if k in EDITABLE_ENV_KEYS}


@router.put("/config")
async def update_config(current_user: CurrentUser, data: dict):
    _check_admin(current_user)
    invalid = set(data.keys()) - EDITABLE_ENV_KEYS
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"These keys are not editable via the admin panel: {sorted(invalid)}",
        )

    env_path = Path(".env")
    if not env_path.exists():
        env_path.touch()

    for key, value in data.items():
        set_key(str(env_path), key, str(value))
        os.environ[key] = str(value)  # apply in-process immediately

    return {
        "message": "Config updated. Changes to email/URL settings take effect immediately. Storage and auth settings require a server restart.",
        "updated": list(data.keys()),
    }


# ---------------------------------------------------------------------------
# User management
# ---------------------------------------------------------------------------

class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    appraisal_role: str = "faculty"
    school: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    employee_id: Optional[str] = None
    phone: Optional[str] = None
    qualification: Optional[str] = None
    teaching_experience: Optional[str] = None
    is_verified: bool = True  # admin-created accounts skip email verification


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    appraisal_role: Optional[str] = None
    school: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    employee_id: Optional[str] = None
    phone: Optional[str] = None
    qualification: Optional[str] = None
    teaching_experience: Optional[str] = None
    is_verified: Optional[bool] = None
    password: Optional[str] = None  # if set, resets the user's password


@router.get("/users")
async def list_users(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    school: Optional[str] = None,
    role: Optional[str] = None,
    search: Optional[str] = None,
):
    _check_admin(current_user)
    query = select(FacultyProfile).order_by(FacultyProfile.school, FacultyProfile.full_name)
    if school:
        query = query.where(FacultyProfile.school == school)
    if role:
        query = query.where(FacultyProfile.appraisal_role == role)
    if search:
        term = f"%{search}%"
        query = query.where(
            FacultyProfile.email.ilike(term) | FacultyProfile.full_name.ilike(term)
        )

    result = await db.execute(query)
    users = result.scalars().all()
    return [
        {
            "email": u.email,
            "full_name": u.full_name,
            "appraisal_role": u.appraisal_role,
            "school": u.school,
            "department": u.department,
            "designation": u.designation,
            "employee_id": u.employee_id,
            "phone": u.phone,
            "qualification": u.qualification,
            "teaching_experience": u.teaching_experience,
            "is_verified": u.is_verified,
            "created_at": u.created_at,
        }
        for u in users
    ]


@router.post("/users", status_code=201)
async def create_user(
    current_user: CurrentUser,
    data: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    _check_admin(current_user)

    if data.appraisal_role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role '{data.appraisal_role}'. Valid roles: {sorted(VALID_ROLES)}",
        )

    existing = await db.execute(select(FacultyProfile).where(FacultyProfile.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = FacultyProfile(
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
        is_verified=data.is_verified,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"message": "User created", "email": user.email, "role": user.appraisal_role}


@router.put("/users/{email}")
async def update_user(
    email: str,
    current_user: CurrentUser,
    data: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    _check_admin(current_user)

    if data.appraisal_role is not None and data.appraisal_role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role '{data.appraisal_role}'. Valid roles: {sorted(VALID_ROLES)}",
        )

    result = await db.execute(select(FacultyProfile).where(FacultyProfile.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updates = data.model_dump(exclude_none=True)
    if "password" in updates:
        user.password_hash = get_password_hash(updates.pop("password"))
    for field, value in updates.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return {"message": "User updated", "email": user.email, "role": user.appraisal_role}


@router.delete("/users/{email}")
async def delete_user(
    email: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _check_admin(current_user)

    result = await db.execute(select(FacultyProfile).where(FacultyProfile.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()
    return {"message": f"User {email} deleted"}
