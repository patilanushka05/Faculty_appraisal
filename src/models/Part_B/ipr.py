from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum, Double, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from src.setup.database import Base

class IPR(Base):
    __tablename__ = "ipr"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty.id"))
    title = Column(Text, nullable=False)
    scope = Column(String(20), nullable=False) # National / International
    filing_date = Column(Date, name="date_of_filing", nullable=False)
    status = Column(String(50), nullable=False) # Published / Granted
    patent_file_no = Column(String(100), nullable=False)
    api_score_faculty = Column(Double, name="research_score_faculty", default=0.0)
    api_score_hod = Column(Double, name="research_score_hod", default=0.0)
    api_score_director = Column(Double, name="research_score_director", default=0.0)
    api_score_dean = Column(Double, name="dean_score", default=0.0)
    api_score_vc = Column(Double, name="vc_score", default=0.0)
    department = Column(String, nullable=True)
    document = Column(String, nullable=True)

    faculty = relationship("Faculty", back_populates="ipr_entries")
