"""Email delivery via Resend. Degrades gracefully when RESEND_API_KEY is
not configured: the caller can still generate the PDF, but sending is
reported as skipped/pending configuration rather than raising."""
import base64
import logging

from flask import current_app

logger = logging.getLogger(__name__)


class EmailNotConfiguredError(Exception):
    pass


def is_email_configured():
    return bool(current_app.config.get("RESEND_API_KEY")) and bool(
        current_app.config.get("RESEND_FROM_EMAIL")
    )


def send_report_email(recipient, subject, message, pdf_bytes, pdf_filename):
    """Sends the PDF report via Resend.

    Returns (status, error) where status is one of 'sent', 'failed', 'skipped'.
    """
    if not is_email_configured():
        logger.info("Resend not configured; skipping email send to %s", recipient)
        return "skipped", "Resend no está configurado (RESEND_API_KEY / RESEND_FROM_EMAIL faltantes)."

    try:
        import resend

        resend.api_key = current_app.config["RESEND_API_KEY"]
        from_name = current_app.config.get("RESEND_FROM_NAME", "Cyber & Privacy Assessment Platform")
        from_email = current_app.config["RESEND_FROM_EMAIL"]

        attachment_b64 = base64.b64encode(pdf_bytes).decode("utf-8")

        params = {
            "from": f"{from_name} <{from_email}>",
            "to": [recipient],
            "subject": subject,
            "html": f"<p>{message}</p>" if message else "<p>Adjunto encontrará el informe de evaluación.</p>",
            "attachments": [
                {
                    "filename": pdf_filename,
                    "content": list(base64.b64decode(attachment_b64)),
                }
            ],
        }
        resend.Emails.send(params)
        return "sent", None
    except Exception as exc:  # noqa: BLE001 - external service failure must not crash the app
        logger.exception("Failed to send report email via Resend")
        return "failed", str(exc)
