from datetime import datetime, timezone
from io import BytesIO

from flask import Blueprint, render_template, redirect, url_for, flash, send_file
from flask_login import login_required, current_user

from app.extensions import db
from app.forms import SendReportForm
from app.utils import get_assessment_or_403
from app.services.audit_service import log_action
from app.services.pdf_service import generate_pdf_bytes
from app.services.email_service import send_report_email, is_email_configured
from app.models.report import EmailLog

reports_bp = Blueprint("reports", __name__, url_prefix="/assessments/<int:assessment_id>/report")


@reports_bp.route("/pdf")
@login_required
def download_pdf(assessment_id):
    assessment = get_assessment_or_403(assessment_id)
    pdf_bytes = generate_pdf_bytes(assessment)
    log_action("generate_report", entity="assessment", entity_id=assessment.id)
    filename = f"informe_{assessment.organization.legal_name}_{assessment.id}.pdf".replace(" ", "_")
    return send_file(BytesIO(pdf_bytes), mimetype="application/pdf", as_attachment=True, download_name=filename)


@reports_bp.route("/send", methods=["GET", "POST"])
@login_required
def send_report(assessment_id):
    assessment = get_assessment_or_403(assessment_id)
    form = SendReportForm()
    email_configured = is_email_configured()

    if form.validate_on_submit():
        pdf_bytes = generate_pdf_bytes(assessment)
        filename = f"informe_{assessment.organization.legal_name}_{assessment.id}.pdf".replace(" ", "_")
        status, error = send_report_email(form.recipient.data, form.subject.data, form.message.data, pdf_bytes, filename)

        entry = EmailLog(
            assessment_id=assessment.id,
            recipient=form.recipient.data,
            subject=form.subject.data,
            message=form.message.data,
            status=status,
            error=error,
        )
        db.session.add(entry)
        db.session.commit()
        log_action("send_report", entity="assessment", entity_id=assessment.id, detail=f"to={form.recipient.data} status={status}")

        if status == "sent":
            flash("Informe enviado correctamente.", "success")
        elif status == "skipped":
            flash("El envío por correo está pendiente de configuración (Resend no configurado). El PDF puede descargarse manualmente.", "warning")
        else:
            flash(f"No se pudo enviar el informe: {error}", "danger")
        return redirect(url_for("reports.send_report", assessment_id=assessment.id))

    if not form.subject.data:
        form.subject.data = f"Informe de evaluación - {assessment.organization.display_name}"
    if not form.recipient.data and assessment.organization.contact_email:
        form.recipient.data = assessment.organization.contact_email

    logs = EmailLog.query.filter_by(assessment_id=assessment.id).order_by(EmailLog.sent_at.desc()).all()
    return render_template(
        "reports/send.html", form=form, assessment=assessment, email_configured=email_configured, logs=logs
    )
