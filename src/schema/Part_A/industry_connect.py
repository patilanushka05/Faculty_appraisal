from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class IndustryConnectBase(BaseModel):
    sr_no: Optional[int] = None
    industry_name: str = Field(..., max_length=255)
    details_of_activity: str
    department: Optional[str] = None
    document: Optional[str] = None

class IndustryConnectCreate(IndustryConnectBase):
    pass

class IndustryConnectUpdateFaculty(BaseModel):
    industry_name: Optional[str] = Field(None, max_length=255)
    details_of_activity: Optional[str] = None
    api_score_faculty: Optional[float] = None
    department: Optional[str] = None

class IndustryConnectUpdateHOD(BaseModel):
    api_score_hod: float

class IndustryConnectUpdateDirector(BaseModel):
    api_score_director: float

class IndustryConnectUpdateDean(BaseModel):
    api_score_dean: float

class IndustryConnectUpdateVC(BaseModel):
    api_score_vc: float

class IndustryConnectResponse(IndustryConnectBase):
    id: UUID
    faculty_id: UUID
    api_score_faculty: float
    api_score_hod: float
    api_score_director: float
    api_score_dean: float
    api_score_vc: float

    class Config:
        from_attributes = True
