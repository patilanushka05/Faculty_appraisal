from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional, List
from datetime import date, datetime

class NonTeachingAppraisalBase(BaseModel):
    academic_year: str
    joining_date: Optional[date] = None
    designation: Optional[str] = None
    department_section: Optional[str] = None
    experience_dypiu: Optional[float] = 0.0
    total_experience: Optional[float] = 0.0
    current_qualifications: Optional[str] = None
    new_qualifications: Optional[str] = None
    reporting_head: Optional[str] = None
    other_info: Optional[str] = None

class NonTeachingAppraisalCreate(NonTeachingAppraisalBase):
    pass

class NonTeachingSelfAppraisalUpdate(BaseModel):
    responsibilities_staff: float
    contributions_staff: float
    achievements_staff: float
    staff_signature_date: Optional[date] = None

class NonTeachingSectionHeadAssessmentUpdate(BaseModel):
    # Part A Marks
    responsibilities_sh: float
    contributions_sh: float
    achievements_sh: float
    
    # Part B Professional Competence
    pc_knowledge_rules: int
    pc_organize_work: int
    pc_additional_assignments: int
    pc_creativity_innovation: int
    pc_learn_new_duties: int
    
    # Quality of Work
    qw_maintain_records: int
    qw_accuracy_speed: int
    qw_neatness_tidiness: int
    qw_completion_time: int
    qw_diligence_responsibility: int
    
    # Personal Characteristics
    ph_reliability: int
    ph_attitude_respect: int
    ph_discipline: int
    ph_team_work: int
    ph_integrity_behavior: int
    ph_interpersonal_relations: int
    
    # Regularity
    rg_attendance_punctuality: int
    rg_leave_discipline: int
    rg_communication: int
    rg_adherence_hours: int
    rg_responsibility_absence: int
    
    # Final
    sh_recommendation: Optional[str] = None
    sh_grade: Optional[str] = None
    sh_signature_date: Optional[date] = None

class NonTeachingRegistrarReviewUpdate(BaseModel):
    responsibilities_registrar: float
    contributions_registrar: float
    achievements_registrar: float
    registrar_recommendation: Optional[str] = None
    registrar_grade: Optional[str] = None
    registrar_signature_date: Optional[date] = None

class NonTeachingVCFinalizeUpdate(BaseModel):
    vc_final_grade: str
    vc_remarks: Optional[str] = None
    vc_signature_date: Optional[date] = None

class NonTeachingAppraisalResponse(NonTeachingAppraisalBase):
    id: UUID
    staff_id: UUID
    status: str
    
    # Part A Triple Audit
    responsibilities_staff: Optional[float] = 0.0
    contributions_staff: Optional[float] = 0.0
    achievements_staff: Optional[float] = 0.0
    
    responsibilities_sh: Optional[float] = 0.0
    contributions_sh: Optional[float] = 0.0
    achievements_sh: Optional[float] = 0.0
    
    responsibilities_registrar: Optional[float] = 0.0
    contributions_registrar: Optional[float] = 0.0
    achievements_registrar: Optional[float] = 0.0
    
    # Part B
    pc_knowledge_rules: Optional[int] = 0
    pc_organize_work: Optional[int] = 0
    pc_additional_assignments: Optional[int] = 0
    pc_creativity_innovation: Optional[int] = 0
    pc_learn_new_duties: Optional[int] = 0
    qw_maintain_records: Optional[int] = 0
    qw_accuracy_speed: Optional[int] = 0
    qw_neatness_tidiness: Optional[int] = 0
    qw_completion_time: Optional[int] = 0
    qw_diligence_responsibility: Optional[int] = 0
    ph_reliability: Optional[int] = 0
    ph_attitude_respect: Optional[int] = 0
    ph_discipline: Optional[int] = 0
    ph_team_work: Optional[int] = 0
    ph_integrity_behavior: Optional[int] = 0
    ph_interpersonal_relations: Optional[int] = 0
    rg_attendance_punctuality: Optional[int] = 0
    rg_leave_discipline: Optional[int] = 0
    rg_communication: Optional[int] = 0
    rg_adherence_hours: Optional[int] = 0
    rg_responsibility_absence: Optional[int] = 0

    # Final decision fields
    sh_recommendation: Optional[str] = None
    sh_grade: Optional[str] = None
    sh_signature_date: Optional[date] = None
    
    registrar_recommendation: Optional[str] = None
    registrar_grade: Optional[str] = None
    registrar_signature_date: Optional[date] = None
    
    vc_final_grade: Optional[str] = None
    vc_remarks: Optional[str] = None
    vc_signature_date: Optional[date] = None

    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)
