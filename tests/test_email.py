from app.services.email_service import send_report_email, is_email_configured


def test_email_not_configured_returns_skipped(app):
    app.config["RESEND_API_KEY"] = ""
    app.config["RESEND_FROM_EMAIL"] = ""
    with app.app_context():
        assert is_email_configured() is False
        status, error = send_report_email("test@example.com", "Asunto", "Mensaje", b"%PDF-fake", "informe.pdf")
        assert status == "skipped"
        assert error is not None


def test_email_configured_flag_true_when_keys_present(app):
    app.config["RESEND_API_KEY"] = "re_test_key"
    app.config["RESEND_FROM_EMAIL"] = "noreply@example.com"
    with app.app_context():
        assert is_email_configured() is True


def test_send_report_route_marks_skipped_without_configuration(client, seeded, app):
    from tests.conftest import login
    from app.models.assessment import Assessment
    from app.models.report import EmailLog

    app.config["RESEND_API_KEY"] = ""
    app.config["RESEND_FROM_EMAIL"] = ""

    login(client, "admin@demo-corp.ec")
    with app.app_context():
        assessment_id = Assessment.query.first().id

    resp = client.post(
        f"/assessments/{assessment_id}/report/send",
        data={"recipient": "cliente@demo-corp.ec", "subject": "Informe", "message": "Hola"},
        follow_redirects=True,
    )
    assert resp.status_code == 200

    with app.app_context():
        log = EmailLog.query.filter_by(assessment_id=assessment_id).first()
        assert log is not None
        assert log.status == "skipped"
