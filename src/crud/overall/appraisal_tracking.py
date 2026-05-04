from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional
from ...models.Part_B.faculty import Faculty
from ...models.overall.school import School
from ...models.overall.appraisal_summary import AppraisalSummary, AppraisalStatus

async def get_subordinates_status(
    db: AsyncSession, 
    role: str, 
    school_id: Optional[str] = None, 
    department: Optional[str] = None, 
    division: Optional[str] = None
) -> List[dict]:
    """
    Fetches all subordinates based on the current user's hierarchy and their form status.
    """
    query = select(Faculty, AppraisalSummary).outerjoin(
        AppraisalSummary, Faculty.id == AppraisalSummary.faculty_id
    ).join(School, Faculty.school_id == School.id)
    
    if role == "vc":
        # Sees everyone
        pass
    elif role == "dean":
        # Only within their division
        query = query.filter(School.division == division)
    elif role == "director":
        # Only within their school
        query = query.filter(Faculty.school_id == school_id)
    elif role == "hod":
        # Only within their department and school
        query = query.filter(Faculty.school_id == school_id, Faculty.department == department)
    else:
        return []

    result = await db.execute(query)
    results = result.all()
    
    subordinates = []
    for faculty, summary in results:
        subordinates.append({
            "id": faculty.id,
            "name": faculty.name,
            "email": faculty.email,
            "department": faculty.department,
            "school_name": faculty.school.name if faculty.school else "N/A",
            "status": summary.status if summary else "Pending",
            "overall_score": summary.overall_score if summary else 0.0,
            "last_updated": summary.last_updated if summary else None
        })
        
    return subordinates

async def create_or_update_summary_status(
    db: AsyncSession, 
    faculty_id: str, 
    status: AppraisalStatus, 
    academic_year: str,
    overall_score: float = 0.0
) -> AppraisalSummary:
    result = await db.execute(select(AppraisalSummary).filter(
        AppraisalSummary.faculty_id == faculty_id,
        AppraisalSummary.academic_year == academic_year
    ))
    db_summary = result.scalars().first()
    
    if db_summary:
        db_summary.status = status
        db_summary.overall_score = overall_score
    else:
        db_summary = AppraisalSummary(
            faculty_id=faculty_id,
            status=status,
            academic_year=academic_year,
            overall_score=overall_score
        )
        db.add(db_summary)
    
    await db.commit()
    await db.refresh(db_summary)
    return db_summary
