import asyncio
import uuid
from src.setup.database import AsyncSessionLocal
from src.models.Part_B.faculty import Faculty
from src.models.Part_A import (
    TeachingProcess, CourseFile, TeachingMethods, ProjectPartA,
    QualificationEnhancement, StudentFeedback, DepartmentalActivity,
    UniversityActivity, SocialContribution, IndustryConnect, ACR
)
from src.models.Part_B import (
    JournalPublication, BookPublication, ICTPedagogy,
    ResearchGuidance, ResearchProject, IPR, ResearchAward,
    ConferencePaper, ResearchProposal, ProductDevelopment,
    SelfDevelopmentFDP, IndustrialTraining, PopularWriting
)
from src.models.overall.remarks import (
    AppraisalRemarks, HODRemarks, DirectorRemarks, DeanRemarks, FinalApproval
)
from src.models.overall.finalization import Enclosure, Declaration
from src.models.overall.school import School
from src.models.overall.appraisal_summary import AppraisalSummary
from sqlalchemy import select

async def setup_test_data():
    async with AsyncSessionLocal() as db:
        # Check if faculty exists
        faculty_id = uuid.UUID('00000000-0000-0000-0000-000000000001')
        result = await db.execute(select(Faculty).where(Faculty.id == faculty_id))
        faculty = result.scalars().first()
        
        if not faculty:
            print(f"Creating mock faculty with ID: {faculty_id}")
            faculty = Faculty(
                id=faculty_id,
                name="Mock Faculty",
                email="mock@example.com",
                role="faculty",
                department="Computer Science"
            )
            db.add(faculty)
            try:
                await db.commit()
                print("Mock faculty created successfully.")
            except Exception as e:
                await db.rollback()
                print(f"Failed to create mock faculty: {e}")
        else:
            print("Mock faculty already exists.")

if __name__ == "__main__":
    asyncio.run(setup_test_data())
