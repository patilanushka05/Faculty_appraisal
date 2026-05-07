from pydantic import BaseModel, Field, computed_field
from typing import Optional
from uuid import UUID

class StudentFeedbackBase(BaseModel):
    sr_no: Optional[int] = None
    course_code_name: str = Field(..., max_length=255)
    first_feedback: float = Field(..., ge=0, le=5)
    second_feedback: float = Field(..., ge=0, le=5)
    department: Optional[str] = None
    document: Optional[str] = None

class StudentFeedbackCreate(StudentFeedbackBase):
    pass

class StudentFeedbackUpdateFaculty(BaseModel):
    course_code_name: Optional[str] = Field(None, max_length=255)
    first_feedback: Optional[float] = Field(None, ge=0, le=5)
    second_feedback: Optional[float] = Field(None, ge=0, le=5)
    department: Optional[str] = None

class StudentFeedbackUpdateHOD(BaseModel):
    api_score_hod: float

class StudentFeedbackUpdateDirector(BaseModel):
    api_score_director: float

class StudentFeedbackUpdateDean(BaseModel):
    api_score_dean: float

class StudentFeedbackUpdateVC(BaseModel):
    api_score_vc: float

class StudentFeedbackResponse(StudentFeedbackBase):
    id: UUID
    faculty_id: UUID
    api_score_faculty: float
    api_score_hod: float
    api_score_director: float
    api_score_dean: float
    api_score_vc: float

    class Config:
        from_attributes = True

    @computed_field
    @property
    def average(self) -> float:
        return (self.first_feedback + self.second_feedback) / 2
