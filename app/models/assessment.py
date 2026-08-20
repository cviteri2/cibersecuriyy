from datetime import datetime, timezone
from app.extensions import db

STATUS_DRAFT = "draft"
STATUS_IN_PROGRESS = "in_progress"
STATUS_COMPLETED = "completed"
STATUS_ARCHIVED = "archived"

STATUS_LABELS = {
    STATUS_DRAFT: "Borrador",
    STATUS_IN_PROGRESS: "En progreso",
    STATUS_COMPLETED: "Completada",
    STATUS_ARCHIVED: "Archivada",
}


class Assessment(db.Model):
    __tablename__ = "assessments"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    evaluator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    status = db.Column(db.String(20), default=STATUS_DRAFT, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True)

    organization = db.relationship("Organization", back_populates="assessments")
    evaluator = db.relationship("User")
    responses = db.relationship(
        "Response", back_populates="assessment", cascade="all, delete-orphan"
    )
    risks = db.relationship("Risk", back_populates="assessment", cascade="all, delete-orphan")
    actions = db.relationship("Action", back_populates="assessment", cascade="all, delete-orphan")
    email_logs = db.relationship(
        "EmailLog", back_populates="assessment", cascade="all, delete-orphan"
    )

    def progress_percent(self, total_questions):
        if not total_questions:
            return 0
        answered = len(self.responses)
        return round(min(answered, total_questions) / total_questions * 100, 1)

    def __repr__(self):
        return f"<Assessment {self.name} ({self.status})>"
