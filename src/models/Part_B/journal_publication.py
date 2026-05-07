from sqlalchemy import Column, Integer, String, Text, Double, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from src.setup.database import Base

class IndexingEnum(str, enum.Enum):
    SCOPUS = "Scopus"
    SCI = "SCI"
    SCIE = "SCIE"
    UGC = "UGC"

class JournalPublication(Base):
    __tablename__ = "journal_publications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Note: faculty_id is missing in production journal_publications table
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty.id"), nullable=True) 

    sr_no = Column(Integer, name="row_no")
    title_with_page_nos = Column(String, name="title")
    journal_details = Column(String, name="journal")
    issn_isbn = Column(String, name="issn")
    indexing = Column(String)
    api_score_faculty = Column(Double, name="score", default=0.0)
    api_score_hod = Column(Double, name="hod_score", default=0.0)
    api_score_director = Column(Double, name="director_score", default=0.0)
    api_score_dean = Column(Double, name="dean_score", default=0.0)
    api_score_vc = Column(Double, name="vc_score", default=0.0)
    # department and document also missing in production
    department = Column(String, nullable=True)
    document = Column(String, nullable=True)

    # Relationship to Faculty
    faculty = relationship("Faculty", back_populates="journal_publications")
