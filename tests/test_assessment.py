from tests.conftest import login
from app.extensions import db
from app.models.organization import Organization
from app.models.assessment import Assessment
from app.models.question import Question, ANSWER_YES


def test_create_assessment(client, seeded, app):
    login(client, "admin@demo-corp.ec")
    with app.app_context():
        org_id = Organization.query.first().id

    resp = client.post(
        f"/organizations/{org_id}/assessments/new",
        data={"name": "Evaluación de prueba"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        assessment = Assessment.query.filter_by(name="Evaluación de prueba").first()
        assert assessment is not None
        assert assessment.organization_id == org_id


def test_answer_question_creates_response(client, seeded, app):
    login(client, "admin@demo-corp.ec")
    with app.app_context():
        assessment = Assessment.query.first()
        question = Question.query.first()
        assessment_id, domain_id, question_id = assessment.id, question.domain_id, question.id

    resp = client.post(
        f"/assessments/{assessment_id}/questionnaire/{domain_id}/answer/{question_id}",
        data={"answer": ANSWER_YES, "notes": "Respuesta de prueba"},
        follow_redirects=True,
    )
    assert resp.status_code == 200

    with app.app_context():
        from app.models.response import Response

        response = Response.query.filter_by(assessment_id=assessment_id, question_id=question_id).first()
        assert response is not None
        assert response.answer == ANSWER_YES
        assert response.score == 5


def test_answer_question_updates_existing_response(client, seeded, app):
    login(client, "admin@demo-corp.ec")
    with app.app_context():
        assessment = Assessment.query.first()
        question = Question.query.first()
        assessment_id, domain_id, question_id = assessment.id, question.domain_id, question.id

    client.post(
        f"/assessments/{assessment_id}/questionnaire/{domain_id}/answer/{question_id}",
        data={"answer": "no", "notes": "primero"},
    )
    client.post(
        f"/assessments/{assessment_id}/questionnaire/{domain_id}/answer/{question_id}",
        data={"answer": ANSWER_YES, "notes": "segundo"},
    )

    with app.app_context():
        from app.models.response import Response

        responses = Response.query.filter_by(assessment_id=assessment_id, question_id=question_id).all()
        assert len(responses) == 1
        assert responses[0].answer == ANSWER_YES


def test_questionnaire_overview_shows_progress(client, seeded, app):
    login(client, "admin@demo-corp.ec")
    with app.app_context():
        assessment_id = Assessment.query.first().id

    resp = client.get(f"/assessments/{assessment_id}/questionnaire")
    assert resp.status_code == 200
