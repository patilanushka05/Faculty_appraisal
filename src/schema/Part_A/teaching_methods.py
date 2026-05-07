from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class TeachingMethodsBase(BaseModel):
    sr_no: Optional[int] = None
    short_description: str = Field(..., max_length=255)
    details_proof: bool = False
    department: Optional[str] = None
    document: Optional[str] = None

class TeachingMethodsCreate(TeachingMethodsBase):
    pass

class TeachingMethodsUpdateFaculty(BaseModel):
    short_description: Optional[str] = Field(None, max_length=255)
    details_proof: Optional[bool] = None
    department: Optional[str] = None

class TeachingMethodsUpdateHOD(BaseModel):
    api_score_hod: float
    signature: Optional[bool] = None

class TeachingMethodsUpdateDirector(BaseModel):
    api_score_director: float

class TeachingMethodsUpdateDean(BaseModel):
    api_score_dean: float

class TeachingMethodsUpdateVC(BaseModel):
    api_score_vc: float

class TeachingMethodsResponse(TeachingMethodsBase):
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
