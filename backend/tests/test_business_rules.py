"""Business-rule coverage for the three workshops."""

from app import domain
from app.services import budget_service, occupation_file_service, rehabilitation_service


def building(**over):
    base = dict(
        id="b1",
        status=domain.NEW,
        hasDamageImages=True,
        hasEngineerReport=True,
        eligibilityChecked=True,
        apartmentCount=10,
        socialApproval=False,
        budgetRequested=False,
    )
    base.update(over)
    return base


# --- Workshop 2 / Sprint 1: can start rehabilitation --------------------------

def test_rehab_ok_when_all_base_docs_present():
    assert rehabilitation_service.can_start_rehabilitation(building())["canStart"] is True


def test_rehab_blocked_when_missing_photos():
    res = rehabilitation_service.can_start_rehabilitation(building(hasDamageImages=False))
    assert res["canStart"] is False
    assert "תמונות נזק" in res["missing"]


# --- Workshop 2 / Sprint 2: work queue ---------------------------------------

def test_work_queue_needs_engineer_and_eligibility_only():
    assert rehabilitation_service.is_in_work_queue(building(hasDamageImages=False)) is True
    assert rehabilitation_service.is_in_work_queue(building(hasEngineerReport=False)) is False


# --- Workshop 2 / Sprint 3-4: budget eligibility ----------------------------

def test_budget_ok_small_building():
    assert budget_service.check_budget_eligibility(building())["eligible"] is True


def test_budget_blocked_missing_eligibility_check():
    res = budget_service.check_budget_eligibility(building(eligibilityChecked=False))
    assert res["eligible"] is False


def test_budget_large_building_requires_social_approval():
    res = budget_service.check_budget_eligibility(building(apartmentCount=30))
    assert res["eligible"] is False
    assert any("אישור חברתי" in m for m in res["missing"])


def test_budget_large_building_with_social_approval_ok():
    res = budget_service.check_budget_eligibility(
        building(apartmentCount=30, socialApproval=True)
    )
    assert res["eligible"] is True


def test_budget_exactly_24_apartments_is_exempt():
    assert budget_service.check_budget_eligibility(building(apartmentCount=24))["eligible"] is True


# --- Workshop 3: re-occupation file ----------------------------------------

def test_occupation_blocked_without_completed_restoration():
    res = occupation_file_service.can_generate_occupation_file(
        building(budgetRequested=True, status=domain.BUILDING_IN_RESTORATION)
    )
    assert res["eligible"] is False
    assert "סטטוס: תהליך שיקום הסתיים" in res["missing"]


def test_occupation_blocked_without_budget_request():
    res = occupation_file_service.can_generate_occupation_file(
        building(status=domain.RESTORATION_COMPLETED, budgetRequested=False)
    )
    assert res["eligible"] is False


def test_occupation_eligible_when_all_conditions_met():
    res = occupation_file_service.can_generate_occupation_file(
        building(status=domain.RESTORATION_COMPLETED, budgetRequested=True)
    )
    assert res["eligible"] is True
