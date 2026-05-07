from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class TeachingProcessBase(BaseModel):
    sr_no: Optional[int] = None
    semester: str = Field(..., max_length=50)
    course_code_name: str = Field(..., max_length=255)
    planned_classes: int
    conducted_classes: int
    department: Optional[str] = None
    document: Optional[str] = None

class TeachingProcessCreate(TeachingProcessBase):
    pass

class TeachingProcessUpdateFaculty(BaseModel):
    semester: Optional[str] = Field(None, max_length=50)
    course_code_name: Optional[str] = Field(None, max_length=255)
    planned_classes: Optional[int] = None
    conducted_classes: Optional[int] = None
    department: Optional[str] = None

class TeachingProcessUpdateHOD(BaseModel):
    api_score_hod: float
    signature: Optional[bool] = None

class TeachingProcessUpdateDirector(BaseModel):
    api_score_director: float

class TeachingProcessUpdateDean(BaseModel):
    api_score_dean: float

class TeachingProcessUpdateVC(BaseModel):
    api_score_vc: float

class TeachingProcessResponse(TeachingProcessBase):
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
