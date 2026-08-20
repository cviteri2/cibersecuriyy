from datetime import datetime, timezone
from app.extensions import db


class Organization(db.Model):
    __tablename__ = "organizations"

    id = db.Column(db.Integer, primary_key=True)
    legal_name = db.Column(db.String(200), nullable=False)
    trade_name = db.Column(db.String(200))
    tax_id = db.Column(db.String(30))
    sector = db.Column(db.String(120))
    employee_count = db.Column(db.Integer)
    country = db.Column(db.String(100), default="Ecuador")
    city = db.Column(db.String(100))
    contact_name = db.Column(db.String(150))
    contact_email = db.Column(db.String(150))
    contact_phone = db.Column(db.String(40))
    evaluation_date = db.Column(db.Date)
    responsible_evaluator = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    users = db.relationship("User", back_populates="organization")
    assessments = db.relationship(
        "Assessment", back_populates="organization", cascade="all, delete-orphan"
    )

    @property
    def display_name(self):
        return self.trade_name or self.legal_name

    def __repr__(self):
        return f"<Organization {self.legal_name}>"
