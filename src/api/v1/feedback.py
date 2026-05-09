from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.setup.database import get_db
from src.setup.dependencies import CurrentUser
from src.models.core import Feedback
from typing import Optional, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feedback", tags=["Feedback"])

VALID_CATEGORIES = frozenset({"query", "feedback", "bug", "suggestion", "other"})
_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _get_client_ip(request: Request) -> Optional[str]:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def _validate(data: Dict[str, Any]) -> Dict[str, str]:
    errors: Dict[str, str] = {}

    email = (data.get("email") or "").strip()
    category = (data.get("category") or "").strip()
    subject = (data.get("subject") or "").strip()
    message = (data.get("message") or "").strip()
    name = (data.get("name") or "").strip()

    if not email:
        errors["email"] = "Email is required."
    elif len(email) > 254:
        errors["email"] = "Email must be 254 characters or less."
    elif not _EMAIL_RE.match(email):
        errors["email"] = "Enter a valid email address."

    if not category:
        errors["category"] = "Category is required."
    elif category not in VALID_CATEGORIES:
        errors["category"] = f"Category must be one of: {', '.join(sorted(VALID_CATEGORIES))}."

    if not subject:
        errors["subject"] = "Subject is required."
    elif len(subject) > 120:
        errors["subject"] = "Subject must be 120 characters or less."

    if not message:
        errors["message"] = "Message is required."
    elif len(message) > 5000:
        errors["message"] = "Message must be 5000 characters or less."

    if name and len(name) > 80:
        errors["name"] = "Name must be 80 characters or less."

    return errors


def _require_admin(current_user):
    if "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Admin role required")


# --- Public endpoint: anyone can submit ---

@router.post("")
async def create_feedback(request: Request, data: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    errors = _validate(data)
    if errors:
        return JSONResponse(status_code=422, content={"success": False, "errors": errors})

    feedback = Feedback(
        name=(data.get("name") or "").strip() or None,
        email=data["email"].strip().lower(),
        category=data["category"].strip(),
        subject=data["subject"].strip(),
        message=data["message"].strip(),
        ip_address=_get_client_ip(request),
        user_agent=(request.headers.get("user-agent") or "")[:512],
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    return {
        "success": True,
        "message": "Feedback saved.",
        "feedback": {
            "id": str(feedback.id),
            "status": feedback.status,
            "submitted_at": feedback.submitted_at.isoformat(),
        },
    }


# --- Admin-only endpoints ---

@router.get("")
async def list_feedback(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100),
    category: Optional[str] = None,
    status: Optional[str] = None,
):
    _require_admin(current_user)
    query = select(Feedback).order_by(Feedback.submitted_at.desc())
    if category:
        query = query.where(Feedback.category == category)
    if status:
        query = query.where(Feedback.status == status)
    query = query.limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()
    return [
        {
            "id": str(f.id),
            "name": f.name,
            "email": f.email,
            "category": f.category,
            "subject": f.subject,
            "message": f.message,
            "status": f.status,
            "ip_address": f.ip_address,
            "submitted_at": f.submitted_at.isoformat() if f.submitted_at else None,
        }
        for f in items
    ]


@router.get("/{feedback_id}")
async def get_feedback(feedback_id: str, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    _require_admin(current_user)
    result = await db.execute(select(Feedback).where(Feedback.id == feedback_id))
    feedback = result.scalar_one_or_none()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return {
        "id": str(feedback.id),
        "name": feedback.name,
        "email": feedback.email,
        "category": feedback.category,
        "subject": feedback.subject,
        "message": feedback.message,
        "status": feedback.status,
        "ip_address": feedback.ip_address,
        "user_agent": feedback.user_agent,
        "submitted_at": feedback.submitted_at.isoformat() if feedback.submitted_at else None,
    }
