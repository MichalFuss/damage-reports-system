"""
Budget Service — the single source of truth for "may a budget request be
opened for this building?" (Workshop 2, Sprints 3 & 4).

Rules
-----
Base documents (all required):
    * damage photos
    * engineer report
    * eligibility check

Social regulation (Sprint 4):
    * buildings with MORE than 24 apartments also require a social approval
    * buildings with 24 or fewer apartments are exempt
"""

from __future__ import annotations

from ..domain import SOCIAL_APPROVAL_THRESHOLD
from .rehabilitation_service import _missing_base_documents


def check_budget_eligibility(building: dict) -> dict:
    missing = _missing_base_documents(building)

    apartments = int(building.get("apartmentCount", 0) or 0)
    requires_social = apartments > SOCIAL_APPROVAL_THRESHOLD
    if requires_social and not building.get("socialApproval"):
        missing.append(f"אישור חברתי (בניין מעל {SOCIAL_APPROVAL_THRESHOLD} דירות)")

    eligible = not missing
    reason = (
        "ניתן לפתוח בקשת תקציב"
        if eligible
        else "לא ניתן לפתוח בקשת תקציב — חסר: " + ", ".join(missing)
    )
    return {"eligible": eligible, "missing": missing, "reason": reason}
