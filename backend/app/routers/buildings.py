"""
/buildings router — the re-occupation ("תיק אכלוס מחדש") capability from
Workshop 3. A building is the same record as a damage report; this resource
name matches the brief's API (POST /buildings/{id}/return-home-package).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import repository
from ..config import PDF_DIR, PDF_URL_PREFIX
from ..services import occupation_file_service

router = APIRouter(prefix="/buildings", tags=["buildings"])


@router.get("/{building_id}/occupation-eligibility")
def occupation_eligibility(building_id: str):
    building = repository.get_by_id(building_id)
    if not building:
        raise HTTPException(status_code=404, detail="מבנה לא נמצא")
    return occupation_file_service.can_generate_occupation_file(building)


@router.post("/{building_id}/return-home-package")
def generate_return_home_package(building_id: str):
    building = repository.get_by_id(building_id)
    if not building:
        raise HTTPException(status_code=404, detail="מבנה לא נמצא")

    result = occupation_file_service.can_generate_occupation_file(building)
    if not result["eligible"]:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "לא ניתן להפיק תיק אכלוס מחדש",
                "missing": result["missing"],
            },
        )

    try:
        file_name = occupation_file_service.generate_occupation_file(building, PDF_DIR)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail="שגיאה בהפקת המסמך") from exc

    file_url = f"{PDF_URL_PREFIX}/{file_name}"
    repository.set_occupation_file_url(building_id, file_url)
    return {"fileUrl": file_url, "fileName": file_name}
