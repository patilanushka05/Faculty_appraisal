from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

from ...crud.Part_B import (
    journal_publication as crud_journal_publication,
    book_publication as crud_book_publication,
    ict_pedagogy as crud_ict_pedagogy,
    research_guidance as crud_research_guidance,
    research_project as crud_research_project,
    ipr as crud_ipr,
    research_award as crud_research_award,
    conference_paper as crud_conference_paper,
    research_proposal as crud_research_proposal,
    product_development as crud_product_development,
    self_development_fdp as crud_self_development_fdp,
    industrial_training as crud_industrial_training,
    popular_writings as crud_popular_writings,
)
from ...crud.Part_A import (
    teaching_process as crud_teaching_process,
    student_feedback as crud_student_feedback,
    departmental_activities as crud_dept_activity,
    university_activities as crud_univ_activity,
    social_contributions as crud_social,
    industry_connect as crud_industry,
    acr as crud_acr,
    course_file as crud_course_file,
    teaching_methods as crud_teaching_methods,
    project as crud_project,
    qualification_enhancement as crud_qualification,
)
from ...schema.overall.appraisal_summary import PartBSummary, AppraisalSummaryResponse, PartASummary

async def get_appraisal_summary(db: AsyncSession, faculty_id: str) -> AppraisalSummaryResponse:
    # Part B Scores
    journal_score = await crud_journal_publication.get_journal_publications_total_score(db, faculty_id)
    book_score = await crud_book_publication.get_book_publications_total_score(db, faculty_id)
    pedagogy_score = await crud_ict_pedagogy.get_ict_pedagogies_total_score(db, faculty_id)
    guidance_data = await crud_research_guidance.get_research_guidance_total_score(db, faculty_id)
    guidance_score = guidance_data["total_score"]
    project_score = await crud_research_project.get_research_projects_total_score(db, faculty_id)
    ipr_score = await crud_ipr.get_ipr_total_score(db, faculty_id)
    award_score = await crud_research_award.get_research_awards_total_score(db, faculty_id)
    conference_score = await crud_conference_paper.get_conference_papers_total_score(db, faculty_id)
    proposal_score = await crud_research_proposal.get_research_proposals_total_score(db, faculty_id)
    product_score = await crud_product_development.get_product_developments_total_score(db, faculty_id)
    self_development_score = await crud_self_development_fdp.get_self_development_fdp_total_score(db, faculty_id)
    industrial_training_score = await crud_industrial_training.get_industrial_trainings_total_score(db, faculty_id)
    popular_writing_score = await crud_popular_writings.get_popular_writings_total_score(db, faculty_id)

    part_b_total = (
        journal_score + book_score + pedagogy_score + guidance_score +
        project_score + ipr_score + award_score + conference_score +
        proposal_score + product_score + self_development_score + 
        industrial_training_score + popular_writing_score
    )

    part_b_summary = PartBSummary(
        journal_score=journal_score,
        book_score=book_score,
        pedagogy_score=pedagogy_score,
        guidance_score=guidance_score,
        project_score=project_score,
        ipr_score=ipr_score,
        award_score=award_score,
        conference_score=conference_score,
        proposal_score=proposal_score,
        product_score=product_score,
        self_development_score=self_development_score,
        industrial_training_score=industrial_training_score,
        popular_writing_score=popular_writing_score,
        part_b_total=part_b_total,
    )

    # Part A Scores
    # Teaching score is the sum of 5 sub-sections (Total 100 marks) scaled to 25
    tp_score = await crud_teaching_process.get_teaching_process_total_score(db, faculty_id)
    cf_score = await crud_course_file.get_course_file_total_score(db, faculty_id)
    tm_score = await crud_teaching_methods.get_teaching_methods_total_score(db, faculty_id)
    pj_score = await crud_project.get_project_total_score(db, faculty_id)
    qe_score = await crud_qualification.get_qualification_enhancement_total_score(db, faculty_id)
    
    raw_teaching_score = tp_score + cf_score + tm_score + pj_score + qe_score
    teaching_score = min(raw_teaching_score, 100.0) * 0.25 # Scale to 25

    feedback_avg = await crud_student_feedback.get_student_feedback_total_score(db, faculty_id)
    # Assuming feedback_avg is already the overall average (0-5)
    feedback_score = feedback_avg * 17.0 # Scale to 85

    dept_score = min(await crud_dept_activity.get_departmental_activity_total_score(db, faculty_id), 20.0)
    university_score = min(await crud_univ_activity.get_university_activity_total_score(db, faculty_id), 30.0)
    social_score = min(await crud_social.get_social_contribution_total_score(db, faculty_id), 10.0)
    industry_score = min(await crud_industry.get_industry_connect_total_score(db, faculty_id), 5.0)
    acr_score = min(await crud_acr.get_acr_total_score(db, faculty_id), 25.0)

    part_a_total = (
        teaching_score + feedback_score + dept_score + university_score +
        social_score + industry_score + acr_score
    )

    part_a_summary = PartASummary(
        teaching_score=teaching_score,
        feedback_score=feedback_score,
        dept_score=dept_score,
        university_score=university_score,
        social_score=social_score,
        industry_score=industry_score,
        acr_score=acr_score,
        part_a_total=part_a_total,
    )

    grand_total_score = part_a_total + part_b_total

    return AppraisalSummaryResponse(
        faculty_id=faculty_id,
        part_a_summary=part_a_summary,
        part_b_summary=part_b_summary,
        grand_total_score=grand_total_score,
    )
