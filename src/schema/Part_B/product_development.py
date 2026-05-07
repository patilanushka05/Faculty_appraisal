from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

# Base schema for common attributes
class ProductDevelopmentBase(BaseModel):
    product_description: str = Field(..., max_length=500)
    usage_type: str = Field(..., max_length=50) # Used in Lab / Commercialized
    department: Optional[str] = Field(None, description="Department of the faculty") # Added as per user request
    document: Optional[str] = Field(None, description="Google Drive link to the document") # Added as per user request

# Schema for creating a new Product Development entry (Faculty input)
class ProductDevelopmentCreate(ProductDevelopmentBase):
    pass

# Schema for faculty to update their own Product Development entry
class ProductDevelopmentUpdateFaculty(ProductDevelopmentBase):
    product_description: Optional[str] = Field(None, max_length=500)
    usage_type: Optional[str] = Field(None, max_length=50)

# Schema for HOD to update API score
class ProductDevelopmentUpdateHOD(BaseModel):
    api_score_hod: float

# Schema for Director to update API score
class ProductDevelopmentUpdateDirector(BaseModel):
    api_score_director: float

# Schema for API response

class ProductDevelopmentUpdateDean(BaseModel):
    api_score_dean: float

class ProductDevelopmentUpdateVC(BaseModel):
    api_score_vc: float

class ProductDevelopmentResponse(ProductDevelopmentBase):
    id: UUID
    faculty_id: UUID
    api_score_faculty: int
    api_score_hod: float
    api_score_vc: float
    api_score_dean: float
    api_score_director: float

    class Config:
        from_attributes = True

# Schema for total score summary
class ProductDevelopmentSummary(BaseModel):
    total_score: float
