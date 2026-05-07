from sqlalchemy import Column, String, Numeric, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime
from src.setup.database import Base

class NonTeachingAppraisal(Base):
    __tablename__ = "non_teaching_appraisals"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    staff_email = Column(String, nullable=False)
    academic_year = Column(String, nullable=False)
    payload = Column(JSONB, nullable=False)
    status = Column(String, nullable=False, default='Draft')
    self_total = Column(Numeric, nullable=False, default=0)
    ro_total = Column(Numeric, nullable=False, default=0)
    registrar_total = Column(Numeric, nullable=False, default=0)
    vc_total = Column(Numeric, nullable=False, default=0)
    submitted_at = Column(DateTime(timezone=True))
    ro_reviewed_at = Column(DateTime(timezone=True))
    registrar_reviewed_at = Column(DateTime(timezone=True))
    vc_reviewed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class NonTeachingPartAItem(Base):
    __tablename__ = "non_teaching_part_a_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    staff_email = Column(String, nullable=False)
    academic_year = Column(String, nullable=False)
    item_key = Column(String, nullable=False)
    title = Column(String, nullable=False)
    max_marks = Column(Numeric, nullable=False)
    details = Column(String)
    self_marks = Column(Numeric)
    ro_marks = Column(Numeric)
    registrar_marks = Column(Numeric)
    vc_marks = Column(Numeric)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class NonTeachingPartBRating(Base):
    __tablename__ = "non_teaching_part_b_ratings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    staff_email = Column(String, nullable=False)
    academic_year = Column(String, nullable=False)
    section_key = Column(String, nullable=False)
    section_title = Column(String, nullable=False)
    max_marks = Column(Numeric, nullable=False)
    parameter_no = Column(Integer, nullable=False)
    parameter_label = Column(String, nullable=False)
    ro_rating = Column(Numeric)
    registrar_rating = Column(Numeric)
    vc_rating = Column(Numeric)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
