"""
Occupation File Service — "הפקת תיק אכלוס מחדש" (Workshop 3, Crisis Load).

Owns:
  * the eligibility rule for producing a re-occupation file
  * orchestration of the PDF generation

Eligibility (all required):
  * engineer report
  * eligibility check
  * an open budget request
  * status == RESTORATION_COMPLETED  (תהליך שיקום הסתיים)

The budget/rehabilitation rules are NOT duplicated here — this module only
adds the two conditions unique to the re-occupation flow.
"""

from __future__ import annotations

from ..domain import RESTORATION_COMPLETED
from ..pdf.occupation_pdf import build_occupation_pdf


def can_generate_occupation_file(building: dict) -> dict:
    missing: list[str] = []
    if not building.get("hasEngineerReport"):
        missing.append("דו\"ח מהנדס")
    if not building.get("eligibilityChecked"):
        missing.append("בדיקת זכאות")
    if not building.get("budgetRequested"):
        missing.append("בקשת תקציב")
    if building.get("status") != RESTORATION_COMPLETED:
        missing.append("סטטוס: תהליך שיקום הסתיים")

    eligible = not missing
    return {"eligible": eligible, "missing": missing}


def generate_occupation_file(building: dict, output_dir) -> str:
    """
    Produce the PDF for an already-eligible building and return the file name.
    Caller is responsible for having checked eligibility.
    """
    return build_occupation_pdf(building, output_dir)
