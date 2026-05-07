from sqlalchemy import Column, Integer, String, ForeignKey, Text, Double, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from src.setup.database import Base

class PopularWriting(Base):
    __tablename__ = "popular_writings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty.id"))
    sr_no = Column(Integer, nullable=True)
    title = Column(Text, nullable=False)
    writing_type = Column(String(50), nullable=False) # Popular Writing / Film / Documentary
    publisher_agency = Column(String(255), nullable=True)
    date = Column(Date, nullable=False)
    api_score_faculty = Column(Double, default=0.0)
    api_score_hod = Column(Double, default=0.0)
    api_score_director = Column(Double, default=0.0)
    api_score_dean = Column(Double, default=0.0)
    api_score_vc = Column(Double, default=0.0)
    department = Column(String, nullable=True)
    document = Column(String, nullable=True)

    faculty = relationship("Faculty", back_populates="popular_writings")
