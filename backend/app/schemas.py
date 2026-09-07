"""Pydantic request/response models for the /reports resource."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from .domain import VALID_STATUSES


class ReportCreate(BaseModel):
    reporterName: str = Field(min_length=1)
    address: str = Field(min_length=1)
    damageType: str = Field(min_length=1)
    description: str = Field(min_length=1)

    # Optional checklist fields — a report may be created with them already known.
    hasDamageImages: bool = False
    hasEngineerReport: bool = False
    eligibilityChecked: bool = False
    apartmentCount: int = 0
    socialApproval: bool = False


class ReportDetailsUpdate(BaseModel):
    """Partial update of the checklist / numeric fields (Workshop 2)."""

    hasDamageImages: Optional[bool] = None
    hasEngineerReport: Optional[bool] = None
    eligibilityChecked: Optional[bool] = None
    apartmentCount: Optional[int] = None
    socialApproval: Optional[bool] = None


class StatusUpdate(BaseModel):
    status: str

    def is_valid(self) -> bool:
        return self.status in VALID_STATUSES
