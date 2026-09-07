"""End-to-end API flow tests using FastAPI's TestClient."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def _create(client, **over):
    payload = dict(
        reporterName="בודק",
        address="רחוב הבדיקה 1, תל אביב",
        damageType="נזק מים",
        description="תיאור",
        apartmentCount=10,
    )
    payload.update(over)
    r = client.post("/reports", json=payload)
    assert r.status_code == 201
    return r.json()


def test_new_report_starts_waiting_for_validation(client):
    assert _create(client)["status"] == "WAITING_FOR_VALIDATION"


def test_list_filters_by_work_queue(client):
    _create(client, hasEngineerReport=True, eligibilityChecked=True)
    rows = client.get("/reports?workQueue=true").json()
    assert rows and all(r["inWorkQueue"] for r in rows)


def test_budget_request_blocked_then_allowed(client):
    rep = _create(client, hasDamageImages=True)
    blocked = client.post(f"/reports/{rep['id']}/budget-request")
    assert blocked.status_code == 403

    client.patch(
        f"/reports/{rep['id']}/details",
        json={"hasEngineerReport": True, "eligibilityChecked": True},
    )
    ok = client.post(f"/reports/{rep['id']}/budget-request")
    assert ok.status_code == 200
    assert ok.json()["report"]["budgetRequested"] is True


def test_return_home_package_generates_pdf(client):
    rep = _create(
        client,
        hasDamageImages=True,
        hasEngineerReport=True,
        eligibilityChecked=True,
    )
    client.post(f"/reports/{rep['id']}/budget-request")
    client.patch(f"/reports/{rep['id']}/status", json={"status": "RESTORATION_COMPLETED"})

    r = client.post(f"/buildings/{rep['id']}/return-home-package")
    assert r.status_code == 200
    file_url = r.json()["fileUrl"]
    assert file_url.endswith(".pdf")

    served = client.get(file_url)
    assert served.status_code == 200
    assert served.content[:4] == b"%PDF"


def test_return_home_package_blocked_when_not_completed(client):
    rep = _create(
        client, hasDamageImages=True, hasEngineerReport=True, eligibilityChecked=True
    )
    client.post(f"/reports/{rep['id']}/budget-request")
    r = client.post(f"/buildings/{rep['id']}/return-home-package")
    assert r.status_code == 403
