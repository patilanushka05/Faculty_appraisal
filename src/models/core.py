from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, JSON, DateTime, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from src.setup.database import Base

class FacultyProfile(Base):
    __tablename__ = "faculty_profiles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String)
    employee_id = Column(String)
    full_name = Column(String, nullable=False)
    qualification = Column(String)
    designation = Column(String)
    department = Column(String)
    school = Column(String)
    division = Column(String)
    form_family = Column(String) # standard, media, design
    teaching_experience = Column(String)
    phone = Column(String)
    academic_year = Column(String)
    appraisal_role = Column(String, nullable=False, default='faculty')
    avatar = Column(String)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class FormSectionDefinition(Base):
    __tablename__ = "form_section_definitions"
    code = Column(String, primary_key=True)
    form_family = Column(String, nullable=False)
    part = Column(String, nullable=False)
    section_key = Column(String, nullable=False)
    title = Column(String, nullable=False)
    max_marks = Column(Numeric, nullable=False)
    storage_table = Column(String)
    fields = Column(JSONB, nullable=False, default=[])
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Declaration(Base):
    __tablename__ = "declarations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    faculty_email = Column(String, nullable=False)
    academic_year = Column(String, nullable=False)
    part_a_total = Column(Numeric, nullable=False, default=0)
    part_b_total = Column(Numeric, nullable=False, default=0)
    grand_total = Column(Numeric, nullable=False, default=0)
    status = Column(String, nullable=False, default='Pending Review')
    submitted_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class AppraisalDocument(Base):
    __tablename__ = "appraisal_documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    faculty_email = Column(String, nullable=False)
    academic_year = Column(String, nullable=False)
    form_family = Column(String)
    section = Column(String, nullable=False)
    section_title = Column(String)
    max_marks = Column(Numeric)
    row_no = Column(Integer)
    doc_key = Column(String)
    file_name = Column(String, nullable=False)
    file_type = Column(String)
    file_url = Column(String)
    storage_path = Column(String)
    uploaded_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class AppraisalReview(Base):
    __tablename__ = "appraisal_reviews"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    faculty_email = Column(String, nullable=False)
    academic_year = Column(String, nullable=False)
    reviewer_email = Column(String)
    reviewer_role = Column(String, nullable=False)
    part_a_score = Column(Numeric, nullable=False, default=0)
    part_b_score = Column(Numeric, nullable=False, default=0)
    total_score = Column(Numeric, nullable=False, default=0)
    remarks = Column(String)
    status = Column(String, nullable=False)
    reviewed_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class AppraisalSnapshot(Base):
    __tablename__ = "appraisal_snapshots"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    faculty_email = Column(String, nullable=False)
    academic_year = Column(String, nullable=False)
    payload = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
