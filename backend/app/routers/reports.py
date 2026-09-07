"""
/reports router — every HTTP handler for the damage-report resource.

Business decisions are delegated to the services; no eligibility logic is
inlined here.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from .. import repository
from ..domain import NEW, VALID_STATUSES
from ..schemas import ReportCreate, ReportDetailsUpdate, StatusUpdate
from ..serialize import serialize
from ..services import budget_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("")
def list_reports(
    workQueue: bool = Query(False, description="רק מבנים הממתינים בתור לעבודה"),
    budgetReady: bool = Query(False, description="רק מבנים המוכנים לפתיחת תקציב"),
):
    reports = [serialize(r) for r in repository.get_all()]
    if workQueue:
        reports = [r for r in reports if r["inWorkQueue"]]
    if budgetReady:
        reports = [r for r in reports if r["readyForBudget"]]
    reports.sort(key=lambda r: r["createdAt"], reverse=True)
    return reports


@router.post("", status_code=201)
def create_report(payload: ReportCreate):
    report = repository.create(payload.model_dump())
    return serialize(report, detailed=True)


@router.get("/{report_id}")
def get_report(report_id: str):
    report = repository.get_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="דיווח לא נמצא")
    return serialize(report, detailed=True)


@router.patch("/{report_id}/status")
def update_status(report_id: str, payload: StatusUpdate):
    if not payload.is_valid():
        raise HTTPException(
            status_code=400,
            detail=f"סטטוס לא תקין. ערכים מותרים: {', '.join(VALID_STATUSES)}",
        )
    updated = repository.update_status(report_id, payload.status)
    if not updated:
        raise HTTPException(status_code=404, detail="דיווח לא נמצא")
    return serialize(updated, detailed=True)


@router.patch("/{report_id}/details")
def update_details(report_id: str, payload: ReportDetailsUpdate):
    updated = repository.update_details(report_id, payload.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="דיווח לא נמצא")
    return serialize(updated, detailed=True)


@router.get("/{report_id}/budget-eligibility")
def budget_eligibility(report_id: str):
    report = repository.get_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="דיווח לא נמצא")
    return budget_service.check_budget_eligibility(report)


@router.post("/{report_id}/budget-request")
def open_budget_request(report_id: str):
    report = repository.get_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="דיווח לא נמצא")

    result = budget_service.check_budget_eligibility(report)
    if not result["eligible"]:
        raise HTTPException(
            status_code=403,
            detail={"error": "לא ניתן לפתוח בקשת תקציב", "missing": result["missing"]},
        )

    updated = repository.mark_budget_requested(report_id)
    return {
        "success": True,
        "message": "בקשת התקציב נפתחה בהצלחה",
        "report": serialize(updated, detailed=True),
    }
