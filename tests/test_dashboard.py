from tests.conftest import login
from app.models.assessment import Assessment


def test_executive_dashboard_renders_with_indicators(client, seeded, app):
    login(client, "admin@demo-corp.ec")
    with app.app_context():
        assessment_id = Assessment.query.first().id

    resp = client.get(f"/assessments/{assessment_id}/dashboard")
    assert resp.status_code == 200
    assert "Cybersecurity Score".encode("utf-8") in resp.data
    assert "Privacy Score".encode("utf-8") in resp.data
    assert "Riesgos".encode("utf-8") in resp.data


def test_client_can_view_own_assessment_dashboard(client, seeded, app):
    login(client, "cliente@demo-corp.ec")
    with app.app_context():
        assessment_id = Assessment.query.first().id
    resp = client.get(f"/assessments/{assessment_id}/dashboard")
    assert resp.status_code == 200


def test_risk_matrix_page_renders(client, seeded, app):
    login(client, "admin@demo-corp.ec")
    with app.app_context():
        assessment_id = Assessment.query.first().id
    resp = client.get(f"/assessments/{assessment_id}/risks/matrix")
    assert resp.status_code == 200
