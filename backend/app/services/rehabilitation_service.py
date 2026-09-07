"""
Rehabilitation Service — the single source of truth for the "process" rules
introduced in Workshop 2 (Growing Complexity).

Three questions the rest of the system asks about a building:

  1. can_start_rehabilitation  (Sprint 1)
     needs: damage photos + engineer report + eligibility check

  2. is_in_work_queue          (Sprint 2)
     needs: engineer report + eligibility check

  3. is_ready_for_budget       (Sprint 5)
     needs: damage photos + engineer report + eligibility check

No router or PDF module re-implements these checks — they call this service.
"""

from __future__ import annotations

_PHOTOS = "תמונות נזק"
_ENGINEER = "דו\"ח מהנדס"
_ELIGIBILITY = "בדיקת זכאות"


def _missing_base_documents(building: dict) -> list[str]:
    missing: list[str] = []
    if not building.get("hasDamageImages"):
        missing.append(_PHOTOS)
    if not building.get("hasEngineerReport"):
        missing.append(_ENGINEER)
    if not building.get("eligibilityChecked"):
        missing.append(_ELIGIBILITY)
    return missing


def can_start_rehabilitation(building: dict) -> dict:
    missing = _missing_base_documents(building)
    ok = not missing
    return {
        "canStart": ok,
        "missing": missing,
        "label": "ניתן להתחיל שיקום" if ok else "חסר מידע להתחלת שיקום",
    }


def is_in_work_queue(building: dict) -> bool:
    """Sprint 2 — 'ממתין בתור לעבודה'."""
    return bool(building.get("hasEngineerReport") and building.get("eligibilityChecked"))


def is_ready_for_budget(building: dict) -> bool:
    """Sprint 5 — 'מוכן לפתיחת תקציב'."""
    return not _missing_base_documents(building)
