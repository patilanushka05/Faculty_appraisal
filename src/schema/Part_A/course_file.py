from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class CourseFileBase(BaseModel):
    sr_no: Optional[int] = None
    course_paper: str = Field(..., max_length=255)
    title: str = Field(..., max_length=255)
    details_proof: bool = False
    department: Optional[str] = None
    document: Optional[str] = None

class CourseFileCreate(CourseFileBase):
    pass

class CourseFileUpdateFaculty(BaseModel):
    course_paper: Optional[str] = Field(None, max_length=255)
    title: Optional[str] = Field(None, max_length=255)
    details_proof: Optional[bool] = None
    department: Optional[str] = None

class CourseFileUpdateHOD(BaseModel):
    api_score_hod: float
    signature: Optional[bool] = None

class CourseFileUpdateDirector(BaseModel):
    api_score_director: float

class CourseFileUpdateDean(BaseModel):
    api_score_dean: float

class CourseFileUpdateVC(BaseModel):
    api_score_vc: float

class CourseFileResponse(CourseFileBase):
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
