from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class DepartmentalActivityBase(BaseModel):
    sr_no: Optional[int] = None
    activity: str = Field(..., max_length=255)
    nature_of_activity: str
    department: Optional[str] = None
    document: Optional[str] = None

class DepartmentalActivityCreate(DepartmentalActivityBase):
    pass

class DepartmentalActivityUpdateFaculty(BaseModel):
    activity: Optional[str] = Field(None, max_length=255)
    nature_of_activity: Optional[str] = None
    api_score_faculty: Optional[float] = None
    department: Optional[str] = None

class DepartmentalActivityUpdateHOD(BaseModel):
    api_score_hod: float

class DepartmentalActivityUpdateDirector(BaseModel):
    api_score_director: float

class DepartmentalActivityUpdateDean(BaseModel):
    api_score_dean: float

class DepartmentalActivityUpdateVC(BaseModel):
    api_score_vc: float

class DepartmentalActivityResponse(DepartmentalActivityBase):
    id: UUID
    faculty_id: UUID
    api_score_faculty: float
    api_score_hod: float
    api_score_director: float
    api_score_dean: float
    api_score_vc: float

    class Config:
        from_attributes = True
