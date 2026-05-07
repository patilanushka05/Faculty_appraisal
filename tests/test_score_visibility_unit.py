import pytest
from src.api.utils import mask_scores
from src.setup.dependencies import User
from pydantic import BaseModel
from typing import Optional

# Mock Schema for testing
class MockItem(BaseModel):
    api_score_faculty: float = 10.0
    api_score_hod: float = 20.0
    api_score_director: float = 30.0
    api_score_dean: float = 40.0
    api_score_vc: float = 50.0

def test_faculty_visibility():
    user = User(id="f1", roles=["faculty"])
    item = MockItem()
    masked = mask_scores(item, user)
    assert masked.api_score_faculty == 10.0
    assert masked.api_score_hod == 0.0
    assert masked.api_score_director == 0.0
    assert masked.api_score_dean == 0.0
    assert masked.api_score_vc == 0.0

def test_hod_visibility():
    user = User(id="h1", roles=["hod"])
    item = MockItem()
    masked = mask_scores(item, user)
    assert masked.api_score_faculty == 10.0
    assert masked.api_score_hod == 20.0
    assert masked.api_score_director == 0.0
    assert masked.api_score_dean == 0.0
    assert masked.api_score_vc == 0.0

def test_director_visibility():
    user = User(id="d1", roles=["director"])
    item = MockItem()
    masked = mask_scores(item, user)
    assert masked.api_score_faculty == 10.0
    assert masked.api_score_hod == 0.0
    assert masked.api_score_director == 30.0
    assert masked.api_score_dean == 0.0
    assert masked.api_score_vc == 0.0

def test_dean_visibility():
    user = User(id="de1", roles=["dean"])
    item = MockItem()
    masked = mask_scores(item, user)
    assert masked.api_score_faculty == 10.0
    assert masked.api_score_hod == 0.0
    assert masked.api_score_director == 0.0
    assert masked.api_score_dean == 40.0
    assert masked.api_score_vc == 0.0

def test_vc_visibility():
    user = User(id="vc1", roles=["vc"])
    item = MockItem()
    masked = mask_scores(item, user)
    assert masked.api_score_faculty == 10.0
    assert masked.api_score_hod == 20.0
    assert masked.api_score_director == 30.0
    assert masked.api_score_dean == 40.0
    assert masked.api_score_vc == 50.0

def test_admin_visibility():
    user = User(id="a1", roles=["admin"])
    item = MockItem()
    masked = mask_scores(item, user)
    assert masked.api_score_faculty == 10.0
    assert masked.api_score_hod == 20.0
    assert masked.api_score_director == 30.0
    assert masked.api_score_dean == 40.0
    assert masked.api_score_vc == 50.0

if __name__ == "__main__":
    # Manual run if pytest is not available
    test_faculty_visibility()
    test_hod_visibility()
    test_director_visibility()
    test_dean_visibility()
    test_vc_visibility()
    test_admin_visibility()
    print("All score visibility tests passed!")
