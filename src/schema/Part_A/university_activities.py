from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class UniversityActivityBase(BaseModel):
    sr_no: Optional[int] = None
    activity: str = Field(..., max_length=255)
    nature_of_activity: str
    department: Optional[str] = None
    document: Optional[str] = None

class UniversityActivityCreate(UniversityActivityBase):
    pass

class UniversityActivityUpdateFaculty(BaseModel):
    activity: Optional[str] = Field(None, max_length=255)
    nature_of_activity: Optional[str] = None
    department: Optional[str] = None

class UniversityActivityUpdateHOD(BaseModel):
    api_score_hod: float

class UniversityActivityUpdateDirector(BaseModel):
    api_score_director: float

class UniversityActivityUpdateDean(BaseModel):
    api_score_dean: float

class UniversityActivityUpdateVC(BaseModel):
    api_score_vc: float

class UniversityActivityResponse(UniversityActivityBase):
    id: UUID
    faculty_id: UUID
    api_score_faculty: float
    api_score_hod: float
    api_score_director: float
    api_score_dean: float
    api_score_vc: float

    class Config:
        from_attributes = True
