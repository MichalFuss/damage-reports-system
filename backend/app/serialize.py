"""Turn a stored report into the shape the API/frontend consumes."""

from __future__ import annotations

from .domain import STATUS_LABELS_HE
from .services import budget_service, occupation_file_service, rehabilitation_service


def serialize(report: dict, *, detailed: bool = False) -> dict:
    out = dict(report)
    out["statusLabel"] = STATUS_LABELS_HE.get(report["status"], report["status"])

    rehab = rehabilitation_service.can_start_rehabilitation(report)
    out["rehabilitation"] = rehab
    out["inWorkQueue"] = rehabilitation_service.is_in_work_queue(report)
    out["readyForBudget"] = rehabilitation_service.is_ready_for_budget(report)

    if detailed:
        out["budgetEligibility"] = budget_service.check_budget_eligibility(report)
        out["occupationEligibility"] = occupation_file_service.can_generate_occupation_file(
            report
        )

    return out
