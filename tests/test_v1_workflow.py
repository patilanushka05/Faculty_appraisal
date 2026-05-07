import pytest
from httpx import AsyncClient
from datetime import datetime

@pytest.fixture
async def auth_headers(client: AsyncClient):
    # Setup test user
    email = "workflow_test@test.com"
    password = "password"
    await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Workflow User",
        "appraisal_role": "faculty",
        "school": "SoCSEA"
    })
    
    login_res = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = login_res.json()["token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_appraisal_snapshot_and_submit(client: AsyncClient, auth_headers: dict):
    academic_year = "2025-26"
    
    # 1. Save Snapshot (Draft)
    snapshot_data = {
        "academic_year": academic_year,
        "payload": {
            "form": {
                "lectures": [{"semester": "Sem 1", "course_code": "CS101", "planned_classes": 40, "conducted_classes": 38}],
                "journals": [{"title": "Test Paper", "journal": "Test Journal", "score": 10}]
            },
            "totals": {"partATotal": 10, "partBTotal": 10, "grandTotal": 20}
        }
    }
    
    save_res = await client.put("/api/v1/appraisal/snapshot", json=snapshot_data, headers=auth_headers)
    assert save_res.status_code == 200
    assert save_res.json()["message"] == "Saved"

    # 2. Get Snapshot
    get_res = await client.get(f"/api/v1/appraisal/snapshot?academic_year={academic_year}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["payload"]["form"]["lectures"][0]["course_code"] == "CS101"

    # 3. Submit Appraisal
    submit_data = {
        "academic_year": academic_year,
        "form": snapshot_data["payload"]["form"],
        "totals": snapshot_data["payload"]["totals"]
    }
    submit_res = await client.post("/api/v1/appraisal/submit", json=submit_data, headers=auth_headers)
    assert submit_res.status_code == 200
    assert "Submitted successfully" in submit_res.json()["message"]

    # 4. Check Status
    status_res = await client.get(f"/api/v1/appraisal/status?academic_year={academic_year}", headers=auth_headers)
    assert status_res.status_code == 200
    status_json = status_res.json()
    assert status_json["declaration"]["status"] == "Submitted"
    assert status_json["declaration"]["grand_total"] == 20
