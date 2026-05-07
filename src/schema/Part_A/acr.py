from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class ACRBase(BaseModel):
    sr_no: Optional[int] = None
    subject: str = Field(..., max_length=255)
    department: Optional[str] = None
    document: Optional[str] = None

class ACRCreate(ACRBase):
    faculty_id: str

class ACRUpdateHOD(BaseModel):
    api_score_hod: float
    department: Optional[str] = None

class ACRUpdateDirector(BaseModel):
    api_score_director: float
    signature: Optional[bool] = None

class ACRUpdateDean(BaseModel):
    api_score_dean: float

class ACRUpdateVC(BaseModel):
    api_score_vc: float

class ACRResponse(ACRBase):
    id: UUID
    faculty_id: UUID
    api_score_faculty: float
    api_score_hod: float
    api_score_director: float
    api_score_dean: float
    api_score_vc: float
    signature: bool

    class Config:
        from_attributes = True
