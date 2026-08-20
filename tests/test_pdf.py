from app.models.assessment import Assessment
from app.services.pdf_service import generate_pdf_bytes


def test_generate_pdf_bytes_produces_valid_pdf(app, seeded):
    with app.app_context():
        assessment = Assessment.query.first()
        pdf_bytes = generate_pdf_bytes(assessment)

    assert pdf_bytes[:4] == b"%PDF"
    assert len(pdf_bytes) > 1000


def test_download_pdf_route(client, seeded, app):
    from tests.conftest import login

    login(client, "admin@demo-corp.ec")
    with app.app_context():
        assessment_id = Assessment.query.first().id

    resp = client.get(f"/assessments/{assessment_id}/report/pdf")
    assert resp.status_code == 200
    assert resp.mimetype == "application/pdf"
    assert resp.data[:4] == b"%PDF"
