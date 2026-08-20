from datetime import datetime, timezone
from app.extensions import db

ACTION_STATUS_PENDING = "pending"
ACTION_STATUS_IN_PROGRESS = "in_progress"
ACTION_STATUS_BLOCKED = "blocked"
ACTION_STATUS_COMPLETED = "completed"
ACTION_STATUS_CANCELLED = "cancelled"

ACTION_STATUS_LABELS = {
    ACTION_STATUS_PENDING: "Pendiente",
    ACTION_STATUS_IN_PROGRESS: "En progreso",
    ACTION_STATUS_BLOCKED: "Bloqueada",
    ACTION_STATUS_COMPLETED: "Completada",
    ACTION_STATUS_CANCELLED: "Cancelada",
}

PRIORITY_LOW = "low"
PRIORITY_MEDIUM = "medium"
PRIORITY_HIGH = "high"
PRIORITY_CRITICAL = "critical"

PRIORITY_LABELS = {
    PRIORITY_LOW: "Baja",
    PRIORITY_MEDIUM: "Media",
    PRIORITY_HIGH: "Alta",
    PRIORITY_CRITICAL: "Crítica",
}


class Action(db.Model):
    __tablename__ = "actions"

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessments.id"), nullable=False)
    risk_id = db.Column(db.Integer, db.ForeignKey("risks.id"), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    control_ref = db.Column(db.String(120))
    responsible = db.Column(db.String(150))
    priority = db.Column(db.String(20), default=PRIORITY_MEDIUM)
    start_date = db.Column(db.Date, nullable=True)
    target_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default=ACTION_STATUS_PENDING)
    progress = db.Column(db.Integer, default=0)  # 0-100
    closure_evidence = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    assessment = db.relationship("Assessment", back_populates="actions")
    risk = db.relationship("Risk", back_populates="actions")

    def __repr__(self):
        return f"<Action {self.title}>"
