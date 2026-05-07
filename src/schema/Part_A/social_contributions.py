from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class SocialContributionBase(BaseModel):
    sr_no: Optional[int] = None
    activity_type: str = Field(..., max_length=255)
    details_of_activity: str
    department: Optional[str] = None
    document: Optional[str] = None

class SocialContributionCreate(SocialContributionBase):
    pass

class SocialContributionUpdateFaculty(BaseModel):
    activity_type: Optional[str] = Field(None, max_length=255)
    details_of_activity: Optional[str] = None
    api_score_faculty: Optional[float] = None
    department: Optional[str] = None

class SocialContributionUpdateHOD(BaseModel):
    api_score_hod: float

class SocialContributionUpdateDirector(BaseModel):
    api_score_director: float

class SocialContributionUpdateDean(BaseModel):
    api_score_dean: float

class SocialContributionUpdateVC(BaseModel):
    api_score_vc: float

class SocialContributionResponse(SocialContributionBase):
    id: UUID
    faculty_id: UUID
    api_score_faculty: float
    api_score_hod: float
    api_score_director: float
    api_score_dean: float
    api_score_vc: float

    class Config:
        from_attributes = True
