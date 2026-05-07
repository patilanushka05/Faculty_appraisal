from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional, List, Any
from datetime import datetime

class NonTeachingAppraisalBase(BaseModel):
    staff_email: str
    academic_year: str
    payload: Any = {}
    status: str = 'Draft'
    self_total: float = 0
    ro_total: float = 0
    registrar_total: float = 0
    vc_total: float = 0

class NonTeachingAppraisalResponse(NonTeachingAppraisalBase):
    id: UUID
    submitted_at: Optional[datetime] = None
    ro_reviewed_at: Optional[datetime] = None
    registrar_reviewed_at: Optional[datetime] = None
    vc_reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class NonTeachingPartAItemBase(BaseModel):
    staff_email: str
    academic_year: str
    item_key: str
    title: str
    max_marks: float
    details: Optional[str] = None
    self_marks: Optional[float] = None
    ro_marks: Optional[float] = None
    registrar_marks: Optional[float] = None
    vc_marks: Optional[float] = None

class NonTeachingPartAItemResponse(NonTeachingPartAItemBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class NonTeachingPartBRatingBase(BaseModel):
    staff_email: str
    academic_year: str
    section_key: str
    section_title: str
    max_marks: float
    parameter_no: int
    parameter_label: str
    ro_rating: Optional[float] = None
    registrar_rating: Optional[float] = None
    vc_rating: Optional[float] = None

class NonTeachingPartBRatingResponse(NonTeachingPartBRatingBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
