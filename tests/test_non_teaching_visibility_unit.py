import pytest
from src.api.utils import mask_scores
from src.setup.dependencies import User
from pydantic import BaseModel
from typing import Optional

# Mock Schema for Non-Teaching testing
class MockNonTeachingItem(BaseModel):
    responsibilities_staff: float = 10.0
    responsibilities_sh: float = 20.0
    responsibilities_registrar: float = 30.0
    sh_grade: str = "A"
    registrar_grade: str = "A+"
    vc_final_grade: str = "O"

def test_staff_visibility():
    user = User(id="s1", roles=["staff"])
    item = MockNonTeachingItem()
    masked = mask_scores(item, user)
    assert masked.responsibilities_staff == 10.0
    assert masked.responsibilities_sh == 0.0
    assert masked.responsibilities_registrar == 0.0
    assert masked.sh_grade is None
    assert masked.registrar_grade is None
    assert masked.vc_final_grade is None

def test_section_head_visibility():
    user = User(id="sh1", roles=["section_head"])
    item = MockNonTeachingItem()
    masked = mask_scores(item, user)
    assert masked.responsibilities_staff == 10.0
    assert masked.responsibilities_sh == 20.0
    assert masked.responsibilities_registrar == 0.0
    assert masked.sh_grade == "A"
    assert masked.registrar_grade is None

def test_registrar_visibility():
    user = User(id="r1", roles=["registrar"])
    item = MockNonTeachingItem()
    masked = mask_scores(item, user)
    assert masked.responsibilities_staff == 10.0
    assert masked.responsibilities_sh == 0.0
    assert masked.responsibilities_registrar == 30.0
    assert masked.sh_grade is None
    assert masked.registrar_grade == "A+"

def test_vc_visibility_non_teaching():
    user = User(id="vc1", roles=["vc"])
    item = MockNonTeachingItem()
    masked = mask_scores(item, user)
    assert masked.responsibilities_staff == 10.0
    assert masked.responsibilities_sh == 20.0
    assert masked.responsibilities_registrar == 30.0
    assert masked.sh_grade == "A"
    assert masked.registrar_grade == "A+"
    assert masked.vc_final_grade == "O"

if __name__ == "__main__":
    test_staff_visibility()
    test_section_head_visibility()
    test_registrar_visibility()
    test_vc_visibility_non_teaching()
    print("All Non-Teaching score visibility tests passed!")
