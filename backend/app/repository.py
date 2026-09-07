"""
In-memory repository for damage reports (a.k.a. buildings).

The MVP brief explicitly allows in-memory storage. Everything that touches
the data store lives here so the routers and services never hold raw state.
"""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from . import domain

_lock = threading.Lock()
_reports: dict[str, dict] = {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _days_ago(n: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=n)).isoformat()


def _blank_report() -> dict:
    return {
        "id": str(uuid.uuid4()),
        "reporterName": "",
        "address": "",
        "damageType": "",
        "description": "",
        "status": domain.WAITING_FOR_VALIDATION,
        "createdAt": _now_iso(),
        "hasDamageImages": False,
        "hasEngineerReport": False,
        "eligibilityChecked": False,
        "apartmentCount": 0,
        "socialApproval": False,
        "budgetRequested": False,
        "occupationFileUrl": None,
    }


def create(data: dict) -> dict:
    report = _blank_report()
    report.update(
        {
            "reporterName": data["reporterName"].strip(),
            "address": data["address"].strip(),
            "damageType": data["damageType"].strip(),
            "description": data["description"].strip(),
            "hasDamageImages": bool(data.get("hasDamageImages", False)),
            "hasEngineerReport": bool(data.get("hasEngineerReport", False)),
            "eligibilityChecked": bool(data.get("eligibilityChecked", False)),
            "apartmentCount": int(data.get("apartmentCount", 0) or 0),
            "socialApproval": bool(data.get("socialApproval", False)),
        }
    )
    with _lock:
        _reports[report["id"]] = report
    return dict(report)


def get_all() -> list[dict]:
    with _lock:
        return [dict(r) for r in _reports.values()]


def get_by_id(report_id: str) -> Optional[dict]:
    with _lock:
        row = _reports.get(report_id)
        return dict(row) if row else None


def update_status(report_id: str, status: str) -> Optional[dict]:
    with _lock:
        row = _reports.get(report_id)
        if not row:
            return None
        row["status"] = status
        return dict(row)


def update_details(report_id: str, fields: dict) -> Optional[dict]:
    with _lock:
        row = _reports.get(report_id)
        if not row:
            return None
        for key in (
            "hasDamageImages",
            "hasEngineerReport",
            "eligibilityChecked",
            "socialApproval",
        ):
            if fields.get(key) is not None:
                row[key] = bool(fields[key])
        if fields.get("apartmentCount") is not None:
            row["apartmentCount"] = int(fields["apartmentCount"] or 0)
        return dict(row)


def mark_budget_requested(report_id: str) -> Optional[dict]:
    with _lock:
        row = _reports.get(report_id)
        if not row:
            return None
        row["budgetRequested"] = True
        return dict(row)


def set_occupation_file_url(report_id: str, url: str) -> Optional[dict]:
    with _lock:
        row = _reports.get(report_id)
        if not row:
            return None
        row["occupationFileUrl"] = url
        return dict(row)


# ---------------------------------------------------------------------------
# Seed data — a spread of buildings that exercises every business rule.
# ---------------------------------------------------------------------------

def seed() -> None:
    with _lock:
        if _reports:
            return

    samples = [
        # all base docs, small building -> rehab + budget ready
        dict(
            reporterName="ישראל ישראלי",
            address="רחוב הרצל 10, תל אביב",
            damageType="נזק מים",
            description="צינור פרץ בחדר האמבטיה וגרם לנזק נרחב לתקרה ולרצפה.",
            status=domain.IN_REVIEW,
            createdAt=_days_ago(1),
            hasDamageImages=True, hasEngineerReport=True, eligibilityChecked=True,
            apartmentCount=12, socialApproval=False, budgetRequested=False,
        ),
        # large building WITH social approval -> budget allowed
        dict(
            reporterName="שרה לוי",
            address="שדרות בן גוריון 5, חיפה",
            damageType="נזק אש",
            description="שריפה קטנה במטבח גרמה לנזק לארונות ולתקרה.",
            status=domain.IN_REVIEW,
            createdAt=_days_ago(3),
            hasDamageImages=True, hasEngineerReport=True, eligibilityChecked=True,
            apartmentCount=32, socialApproval=True, budgetRequested=False,
        ),
        # large building, NO social approval -> budget blocked
        dict(
            reporterName="דוד כהן",
            address="רחוב ויצמן 22, ירושלים",
            damageType="נזק רוח",
            description="סערה גרמה לנפילת עץ על גדר הבית ולשבירת חלון.",
            status=domain.IN_REVIEW,
            createdAt=_days_ago(5),
            hasDamageImages=True, hasEngineerReport=True, eligibilityChecked=True,
            apartmentCount=28, socialApproval=False, budgetRequested=False,
        ),
        # missing engineer report -> not in work queue, budget blocked
        dict(
            reporterName="מרים אברהם",
            address="רחוב ביאליק 3, רמת גן",
            damageType="נזק רעידת אדמה",
            description="סדקים נרחבים בקירות הפנימיים ובחיפוי החיצוני.",
            status=domain.NEW,
            createdAt=_days_ago(7),
            hasDamageImages=True, hasEngineerReport=False, eligibilityChecked=True,
            apartmentCount=8, socialApproval=False, budgetRequested=False,
        ),
        # missing eligibility check -> budget blocked
        dict(
            reporterName="יוסף מזרחי",
            address="שדרות רוטשילד 18, תל אביב",
            damageType="נזק פיצוץ",
            description="גז התפוצץ במטבח. נזק לחלונות, דלתות ומערכת חשמל.",
            status=domain.IN_REVIEW,
            createdAt=_days_ago(10),
            hasDamageImages=True, hasEngineerReport=True, eligibilityChecked=False,
            apartmentCount=20, socialApproval=False, budgetRequested=False,
        ),
        # brand new, nothing done yet
        dict(
            reporterName="רחל גולדברג",
            address="רחוב דיזנגוף 44, תל אביב",
            damageType="נזק טיל",
            description="טיל פגע בחצר. נזק למבנה החיצוני ולמרתף.",
            status=domain.WAITING_FOR_VALIDATION,
            createdAt=_days_ago(2),
            hasDamageImages=False, hasEngineerReport=False, eligibilityChecked=False,
            apartmentCount=16, socialApproval=False, budgetRequested=False,
        ),
        # fully restored + budget requested -> eligible for a re-occupation file
        dict(
            reporterName="אמיר שפירא",
            address="רחוב הנשיא 7, נתניה",
            damageType="נזק רסיסים",
            description="רסיסי יירוט פגעו בגג ובחלונות קומה עליונה. השיקום הושלם.",
            status=domain.RESTORATION_COMPLETED,
            createdAt=_days_ago(40),
            hasDamageImages=True, hasEngineerReport=True, eligibilityChecked=True,
            apartmentCount=18, socialApproval=False, budgetRequested=True,
        ),
        # restoration completed but NO budget request -> re-occupation file blocked
        dict(
            reporterName="נועה כץ",
            address="רחוב אלנבי 9, תל אביב",
            damageType="נזק מים",
            description="נזילה מהגג הציפה את חדר המדרגות. השיקום הסתיים.",
            status=domain.RESTORATION_COMPLETED,
            createdAt=_days_ago(35),
            hasDamageImages=True, hasEngineerReport=True, eligibilityChecked=True,
            apartmentCount=24, socialApproval=False, budgetRequested=False,
        ),
        # large building fully restored, social approved, budget requested -> eligible
        dict(
            reporterName="בנימין אזולאי",
            address="שדרות ירושלים 60, אשדוד",
            damageType="נזק טיל",
            description="פגיעה ישירה בחזית. המבנה שוקם במלואו.",
            status=domain.RESTORATION_COMPLETED,
            createdAt=_days_ago(50),
            hasDamageImages=True, hasEngineerReport=True, eligibilityChecked=True,
            apartmentCount=48, socialApproval=True, budgetRequested=True,
        ),
    ]

    with _lock:
        for s in samples:
            report = _blank_report()
            report.update(s)
            _reports[report["id"]] = report
