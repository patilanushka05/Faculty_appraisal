from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Double
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from ...setup.database import Base

class TeachingProcess(Base):
    __tablename__ = "teaching_process"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty.id"))
    sr_no = Column(Integer, nullable=True)
    semester = Column(String(50), nullable=False)
    course_code_name = Column(String(255), nullable=False)
    planned_classes = Column(Integer, name="no_of_classes_planned", nullable=False)
    conducted_classes = Column(Integer, name="no_of_classes_conducted", nullable=False)
    api_score_faculty = Column(Double, default=0.0)
    api_score_hod = Column(Double, default=0.0)
    api_score_director = Column(Double, default=0.0)
    api_score_dean = Column(Double, default=0.0)
    api_score_vc = Column(Double, default=0.0)
    signature = Column(Boolean, default=False)
    department = Column(String, nullable=True)
    document = Column(String, nullable=True)

    faculty = relationship("Faculty", back_populates="teaching_processes")
