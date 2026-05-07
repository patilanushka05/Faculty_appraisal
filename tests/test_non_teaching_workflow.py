from src.setup.dependencies import User, get_current_user
from httpx import AsyncClient, ASGITransport
from main import app
from uuid import uuid4
from datetime import date
import pytest

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_non_teaching_workflow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as client:
        # 1. Mock a staff user and initialize appraisal
        academic_year = "2025-26"
        
        async def get_staff_user(): return User(id="00000000-0000-0000-0000-000000000001", roles=["staff"])
        app.dependency_overrides[get_current_user] = get_staff_user
        
        appraisal_data = {
            "academic_year": academic_year,
            "joining_date": "2020-01-01",
            "designation": "Lab Assistant",
            "department_section": "Computer Science",
            "experience_dypiu": 5.5,
            "total_experience": 10.0,
            "current_qualifications": "B.Sc. IT",
            "reporting_head": "Director CS"
        }
        
        # Staff creates appraisal (Mock user id: 00000000-0000-0000-0000-000000000001)
        response = await client.post("/api/v1/non-teaching/", json=appraisal_data)
        
        # If it already exists, we might get 400. Let's handle that for re-runnability.
        if response.status_code == 400:
            # Try to get existing one
            get_res = await client.get("/api/v1/non-teaching/00000000-0000-0000-0000-000000000001")
            appraisal_id = get_res.json()[0]["id"]
        else:
            assert response.status_code == 201
            appraisal_id = response.json()["id"]
            assert response.json()["status"] == "DRAFT"

        # 2. Staff submits Self-Appraisal (Part A)
        self_appraisal_data = {
            "responsibilities_staff": 8.5,
            "contributions_staff": 7.0,
            "achievements_staff": 4.0,
            "staff_signature_date": "2026-05-01"
        }
        response = await client.patch(f"/api/v1/non-teaching/{appraisal_id}/self-appraisal", json=self_appraisal_data)
        assert response.status_code == 200
        assert response.json()["status"] == "SUBMITTED"

        # 3. Section Head Assessment 
        # (Current mock user has 'faculty' role, so this SHOULD fail with 403 unless we mock the role)
        sh_assessment_data = {
            "responsibilities_sh": 8.0,
            "contributions_sh": 6.5,
            "achievements_sh": 3.5,
            "pc_knowledge_rules": 5, "pc_organize_work": 4, "pc_additional_assignments": 5, "pc_creativity_innovation": 4, "pc_learn_new_duties": 5,
            "qw_maintain_records": 5, "qw_accuracy_speed": 4, "qw_neatness_tidiness": 5, "qw_completion_time": 4, "qw_diligence_responsibility": 5,
            "ph_reliability": 5, "ph_attitude_respect": 5, "ph_discipline": 5, "ph_team_work": 4, "ph_integrity_behavior": 5, "ph_interpersonal_relations": 4,
            "rg_attendance_punctuality": 5, "rg_leave_discipline": 5, "rg_communication": 4, "rg_adherence_hours": 5, "rg_responsibility_absence": 4,
            "sh_recommendation": "Highly recommended for promotion.",
            "sh_grade": "A+",
            "sh_signature_date": "2026-05-05"
        }
        response = await client.patch(f"/api/v1/non-teaching/{appraisal_id}/section-head-assessment", json=sh_assessment_data)
        # Verify it checks roles - currently mock user is 'faculty'
        assert response.status_code == 403 

        # 4. Mock Section Head and submit assessment
        async def get_sh_user(): return User(id="sh_id", roles=["section_head"])
        app.dependency_overrides[get_current_user] = get_sh_user
        
        response = await client.patch(f"/api/v1/non-teaching/{appraisal_id}/section-head-assessment", json=sh_assessment_data)
        assert response.status_code == 200
        
        # 5. Registrar Review
        async def get_registrar_user(): return User(id="reg_id", roles=["registrar"])
        app.dependency_overrides[get_current_user] = get_registrar_user
        
        registrar_data = {
            "responsibilities_registrar": 7.5,
            "contributions_registrar": 6.0,
            "achievements_registrar": 3.0,
            "registrar_recommendation": "Confirmed.",
            "registrar_grade": "A",
            "registrar_signature_date": "2026-05-10"
        }
        response = await client.patch(f"/api/v1/non-teaching/{appraisal_id}/registrar-review", json=registrar_data)
        assert response.status_code == 200
        
        # 6. VC Finalize
        async def get_vc_user(): return User(id="vc_id", roles=["vc"])
        app.dependency_overrides[get_current_user] = get_vc_user
        
        vc_data = {
            "vc_final_grade": "A",
            "vc_remarks": "Good performance.",
            "vc_signature_date": "2026-05-15"
        }
        response = await client.patch(f"/api/v1/non-teaching/{appraisal_id}/vc-finalize", json=vc_data)
        assert response.status_code == 200
        assert response.json()["status"] == "FINALIZED"
        
        app.dependency_overrides.clear()
        
        # 7. Get Appraisal Detail
        response = await client.get("/api/v1/non-teaching/00000000-0000-0000-0000-000000000001")
        assert response.status_code == 200
        assert len(response.json()) > 0
