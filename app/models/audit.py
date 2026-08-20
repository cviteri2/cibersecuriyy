from datetime import datetime, timezone
from app.extensions import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    entity = db.Column(db.String(100))
    entity_id = db.Column(db.Integer, nullable=True)
    detail = db.Column(db.Text)
    ip_address = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User")

    def __repr__(self):
        return f"<AuditLog {self.action} {self.entity}:{self.entity_id}>"
