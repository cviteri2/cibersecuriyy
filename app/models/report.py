from datetime import datetime, timezone
from app.extensions import db

EMAIL_STATUS_SENT = "sent"
EMAIL_STATUS_FAILED = "failed"
EMAIL_STATUS_SKIPPED = "skipped"


class EmailLog(db.Model):
    __tablename__ = "email_logs"

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessments.id"), nullable=False)
    recipient = db.Column(db.String(150), nullable=False)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default=EMAIL_STATUS_SENT)
    error = db.Column(db.Text)
    sent_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    assessment = db.relationship("Assessment", back_populates="email_logs")

    def __repr__(self):
        return f"<EmailLog to={self.recipient} status={self.status}>"
