from sqlalchemy import Column, Integer, String, ForeignKey, Text, Double
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from src.setup.database import Base

class SelfDevelopmentFDP(Base):
    __tablename__ = "self_development"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty.id"))
    program_name = Column(String(255), name="program", nullable=False)
    duration_days = Column(Integer, name="duration", nullable=False)
    organizer = Column(String(255), name="organized_by", nullable=False)
    api_score_faculty = Column(Double, default=0.0)
    api_score_hod = Column(Double, default=0.0)
    api_score_dean = Column(Double, default=0.0)
    api_score_vc = Column(Double, default=0.0)
    api_score_director = Column(Double, default=0.0)
    department = Column(String, nullable=True)
    document = Column(String, nullable=True)

    faculty = relationship("Faculty", back_populates="self_development_fdp_entries")
