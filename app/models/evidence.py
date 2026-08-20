from datetime import datetime, timezone
from app.extensions import db

STATUS_NOT_REQUIRED = "not_required"
STATUS_PENDING = "pending"
STATUS_RECEIVED = "received"
STATUS_VALIDATED = "validated"
STATUS_REJECTED = "rejected"

STATUS_LABELS = {
    STATUS_NOT_REQUIRED: "No requerida",
    STATUS_PENDING: "Pendiente",
    STATUS_RECEIVED: "Recibida",
    STATUS_VALIDATED: "Validada",
    STATUS_REJECTED: "Rechazada",
}


class Evidence(db.Model):
    __tablename__ = "evidences"

    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, db.ForeignKey("responses.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    file_type = db.Column(db.String(20))
    file_path = db.Column(db.String(400))
    responsible = db.Column(db.String(150))
    status = db.Column(db.String(20), default=STATUS_PENDING)
    observations = db.Column(db.Text)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    response = db.relationship("Response", back_populates="evidences")
    uploaded_by = db.relationship("User")

    def __repr__(self):
        return f"<Evidence {self.name}>"
