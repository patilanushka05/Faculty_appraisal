from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated

from ....setup.dependencies import get_db, CurrentUser
from ....schema.Part_A.part_a_summary import PartASummaryResponse
from ....crud.Part_A import (
    teaching_process,
    student_feedback,
    departmental_activities,
    university_activities,
    social_contributions,
    industry_connect,
    acr,
    course_file,
    teaching_methods,
    project,
    qualification_enhancement
)

router = APIRouter()

@router.get("/part-a-summary/{faculty_id}", response_model=PartASummaryResponse)
async def get_part_a_summary(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path()],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=403, detail="Not authorized")

    # Fetch scores from all sections
    tp_entries = await teaching_process.get_teaching_process_by_faculty(db, faculty_id)
    cf_entries = await course_file.get_course_files_by_faculty(db, faculty_id)
    tm_entries = await teaching_methods.get_teaching_methods_by_faculty(db, faculty_id)
    pj_entries = await project.get_projects_by_faculty(db, faculty_id)
    qe_entries = await qualification_enhancement.get_qualification_enhancements_by_faculty(db, faculty_id)
    
    sf_entries = await student_feedback.get_student_feedback_by_faculty(db, faculty_id)
    da_entries = await departmental_activities.get_departmental_activities_by_faculty(db, faculty_id)
    ua_entries = await university_activities.get_university_activities_by_faculty(db, faculty_id)
    sc_entries = await social_contributions.get_social_contributions_by_faculty(db, faculty_id)
    ic_entries = await industry_connect.get_industry_connect_by_faculty(db, faculty_id)
    acr_entries = await acr.get_acr_by_faculty(db, faculty_id)
    
    # 1. Teaching Score (A) - Sum of tp, cf, tm, pj, qe scaled to 25
    # Total marks out of 100 scaled to 25
    raw_teaching_score = (
        sum([e.api_score_faculty for e in tp_entries]) +
        sum([e.api_score_faculty for e in cf_entries]) +
        sum([e.api_score_faculty for e in tm_entries]) +
        sum([e.api_score_faculty for e in pj_entries]) +
        sum([e.api_score_faculty for e in qe_entries])
    )
    teaching_score = min(raw_teaching_score, 100.0) * 0.25 # Scale to 25
    
    # 2. Feedback Score (B) - Average scaled (assuming out of 85 to make Part A total 200)
    feedback_avg = 0.0
    if sf_entries:
        feedback_avg = sum([(e.first_feedback + e.second_feedback)/2 for e in sf_entries]) / len(sf_entries)
    feedback_score = feedback_avg * 17.0 # 5.0 * 17 = 85
    
    # 3. Dept Activity (C) - Max 20
    dept_score = min(sum([e.api_score_faculty for e in da_entries]), 20.0)
    
    # 4. University Activity (D) - Max 30
    univ_score = min(sum([e.api_score_faculty for e in ua_entries]), 30.0)
    
    # 5. Social Score (E) - Max 10
    social_score = min(sum([e.api_score_faculty for e in sc_entries]), 10.0)
    
    # 6. Industry Score (F) - Max 5
    ind_score = min(sum([e.api_score_faculty for e in ic_entries]), 5.0)
    
    # 7. ACR Score (G) - Max 25
    acr_val = min(sum([e.api_score_hod for e in acr_entries]), 25.0)

    # Totals
    total_faculty = teaching_score + feedback_score + dept_score + univ_score + social_score + ind_score + acr_val
    
    # HOD and Director totals (using similar logic)
    raw_hod_teaching = (
        sum([e.api_score_hod for e in tp_entries]) +
        sum([e.api_score_hod for e in cf_entries]) +
        sum([e.api_score_hod for e in tm_entries]) +
        sum([e.api_score_hod for e in pj_entries]) +
        sum([e.api_score_hod for e in qe_entries])
    )
    hod_teaching = min(raw_hod_teaching, 100.0) * 0.25
    hod_total = hod_teaching + acr_val + \
                min(sum([e.api_score_hod for e in da_entries]), 20.0) + \
                min(sum([e.api_score_hod for e in ua_entries]), 30.0) + \
                min(sum([e.api_score_hod for e in sc_entries]), 10.0) + \
                min(sum([e.api_score_hod for e in ic_entries]), 5.0)
    
    # Director total
    raw_dir_teaching = (
        sum([getattr(e, 'api_score_director', 0.0) for e in tp_entries]) +
        sum([getattr(e, 'api_score_director', 0.0) for e in cf_entries]) +
        sum([getattr(e, 'api_score_director', 0.0) for e in tm_entries]) +
        sum([getattr(e, 'api_score_director', 0.0) for e in pj_entries]) +
        sum([getattr(e, 'api_score_director', 0.0) for e in qe_entries])
    )
    dir_teaching = min(raw_dir_teaching, 100.0) * 0.25
    dir_total = dir_teaching + \
                min(sum([getattr(e, 'api_score_director', 0.0) for e in acr_entries]), 25.0) + \
                min(sum([getattr(e, 'api_score_director', 0.0) for e in da_entries]), 20.0) + \
                min(sum([getattr(e, 'api_score_director', 0.0) for e in ua_entries]), 30.0) + \
                min(sum([getattr(e, 'api_score_director', 0.0) for e in sc_entries]), 10.0) + \
                min(sum([getattr(e, 'api_score_director', 0.0) for e in ic_entries]), 5.0)

    return PartASummaryResponse(
        teachingScore=teaching_score,
        feedbackScore=feedback_score,
        deptActivityScore=dept_score,
        universityActivityScore=univ_score,
        socialScore=social_score,
        industryScore=ind_score,
        acrScore=acr_val,
        totalFacultyScore=total_faculty,
        totalHodScore=hod_total,
        totalDirectorScore=dir_total
    )
