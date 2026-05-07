from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from typing import Optional
from datetime import date

class PopularWritingsBase(BaseModel):
    title: str
    writing_type: str
    publisher_agency: Optional[str] = None
    date: date
    sr_no: Optional[int] = None
    department: Optional[str] = None

class PopularWritingsCreate(PopularWritingsBase):
    document: Optional[str] = None

class PopularWritingsUpdateFaculty(BaseModel):
    title: Optional[str] = None
    writing_type: Optional[str] = None
    publisher_agency: Optional[str] = None
    date: Optional[date] = None
    api_score_faculty: Optional[float] = None
    sr_no: Optional[int] = None
    department: Optional[str] = None
    document: Optional[str] = None

class PopularWritingsUpdateHOD(BaseModel):
    api_score_hod: float

class PopularWritingsUpdateDirector(BaseModel):
    api_score_director: float

class PopularWritingsUpdateDean(BaseModel):
    api_score_dean: float

class PopularWritingsUpdateVC(BaseModel):
    api_score_vc: float

class PopularWritingsResponse(PopularWritingsBase):
    id: UUID
    faculty_id: UUID
    api_score_faculty: float
    api_score_hod: float
    api_score_director: float
    api_score_dean: float
    api_score_vc: float
    document: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class PopularWritingsSummary(BaseModel):
    total_score: float
