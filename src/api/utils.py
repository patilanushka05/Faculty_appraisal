from typing import Any, List
from ..setup.dependencies import CurrentUser

def mask_scores(data: Any, current_user: CurrentUser) -> Any:
    """
    Masks score fields based on the user's role.
    Faculty: Can see all.
    HOD: api_score_faculty, api_score_hod.
    Director: api_score_faculty, api_score_director.
    Dean: api_score_faculty, api_score_dean.
    VC/Admin: Can see all.
    """
    if data is None:
        return None

    is_list = isinstance(data, list)
    items = data if is_list else [data]

    roles = current_user.roles
    is_admin_or_vc = any(role in ["admin", "vc"] for role in roles)
    is_faculty = "faculty" in roles
    is_staff = "staff" in roles
    is_hod = "hod" in roles
    is_section_head = "section_head" in roles
    is_director = "director" in roles
    is_dean = "dean" in roles
    is_registrar = "registrar" in roles

    # If admin or VC, they see everything.
    if is_admin_or_vc:
        return data

    for item in items:
        # Determine which score fields to keep based on role
        if is_faculty or is_staff:
            # Faculty/Staff only sees their own scores
            _mask_all_except(item, ["api_score_faculty", "research_score_faculty", 
                                  "responsibilities_staff", "contributions_staff", "achievements_staff"])
        elif is_hod or is_section_head:
            # Level 1: Sees Faculty/Staff + Level 1
            _mask_all_except(item, ["api_score_faculty", "research_score_faculty", "api_score_hod", "research_score_hod",
                                  "responsibilities_staff", "contributions_staff", "achievements_staff",
                                  "responsibilities_sh", "contributions_sh", "achievements_sh",
                                  "sh_recommendation", "sh_grade", "sh_signature_date",
                                  "pc_knowledge_rules", "pc_organize_work", "pc_additional_assignments", 
                                  "pc_creativity_innovation", "pc_learn_new_duties",
                                  "qw_maintain_records", "qw_accuracy_speed", "qw_neatness_tidiness", 
                                  "qw_completion_time", "qw_diligence_responsibility",
                                  "ph_reliability", "ph_attitude_respect", "ph_discipline", "ph_team_work", 
                                  "ph_integrity_behavior", "ph_interpersonal_relations",
                                  "rg_attendance_punctuality", "rg_leave_discipline", "rg_communication", 
                                  "rg_adherence_hours", "rg_responsibility_absence"])
        elif is_director:
            # Level 2 (Director): Sees Faculty + Director
            _mask_all_except(item, ["api_score_faculty", "research_score_faculty", "api_score_director", "research_score_director",
                                  "responsibilities_staff", "contributions_staff", "achievements_staff",
                                  "director_remark", "director_approved_score", "director_signature"])
        elif is_dean or is_registrar:
            # Level 3 (Dean/Registrar): Sees Faculty + Level 3
            _mask_all_except(item, ["api_score_faculty", "research_score_faculty", "api_score_dean", "research_score_dean",
                                  "responsibilities_staff", "contributions_staff", "achievements_staff",
                                  "responsibilities_registrar", "contributions_registrar", "achievements_registrar",
                                  "registrar_recommendation", "registrar_grade", "registrar_signature_date",
                                  "dean_remark", "dean_approved_score", "dean_signature"])
        else:
            # Other roles see only base scores
            _mask_all_except(item, ["api_score_faculty", "research_score_faculty", 
                                  "responsibilities_staff", "contributions_staff", "achievements_staff"])

    return data if is_list else items[0]

def _mask_all_except(item: Any, allowed_fields: List[str]):
    """
    Masks all score-related fields except the ones explicitly allowed.
    """
    all_score_patterns = [
        "api_score_", "research_score_", 
        "responsibilities_", "contributions_", "achievements_",
        "pc_", "qw_", "ph_", "rg_", # Part B Non-Teaching
        "sh_", "registrar_", "vc_"  # Recommendation/Grades
    ]
    
    # We only want to mask IF the field is NOT in allowed_fields
    # For Non-Teaching Part B (pc, qw, ph, rg) and recommendations, we only show them to the role that fills them or VC.
    # Actually, the requirement was "don't see others".
    
    # Get all attributes/keys
    if isinstance(item, dict):
        keys = item.keys()
    else:
        # Pydantic or SQLAlchemy
        keys = item.__dict__.keys() if hasattr(item, "__dict__") else []
        if not keys and hasattr(item, "model_fields"): # Pydantic v2
            keys = item.model_fields.keys()

    for key in keys:
        if any(key.startswith(pat) for pat in all_score_patterns):
            if key not in allowed_fields:
                # Special cases for Non-Teaching Part B and recommendations
                # If you are Section Head, you can see 'sh_' fields.
                # If you are Registrar, you can see 'registrar_' fields.
                # This is handled by allowed_fields if we are careful.
                _set_value(item, key, 0.0 if "score" in key or "responsibilities" in key else None)

def _set_value(item: Any, field_name: str, value: Any):
    if isinstance(item, dict):
        item[field_name] = value
    else:
        setattr(item, field_name, value)

def _set_score(item: Any, field_name: str, value: float):
    # Keep for backward compatibility if needed, but we used _mask_all_except now
    _set_value(item, field_name, value)
