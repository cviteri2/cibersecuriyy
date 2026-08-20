from datetime import datetime, timezone
from app.extensions import db

TREATMENT_MITIGATE = "mitigate"
TREATMENT_TRANSFER = "transfer"
TREATMENT_AVOID = "avoid"
TREATMENT_ACCEPT = "accept"

TREATMENT_LABELS = {
    TREATMENT_MITIGATE: "Mitigar",
    TREATMENT_TRANSFER: "Transferir",
    TREATMENT_AVOID: "Evitar",
    TREATMENT_ACCEPT: "Aceptar",
}

RISK_STATUS_OPEN = "open"
RISK_STATUS_IN_TREATMENT = "in_treatment"
RISK_STATUS_CLOSED = "closed"

RISK_STATUS_LABELS = {
    RISK_STATUS_OPEN: "Abierto",
    RISK_STATUS_IN_TREATMENT: "En tratamiento",
    RISK_STATUS_CLOSED: "Cerrado",
}


def risk_level(score):
    if score is None:
        return None
    if score <= 4:
        return "low"
    if score <= 9:
        return "medium"
    if score <= 16:
        return "high"
    return "critical"


RISK_LEVEL_LABELS = {
    "low": "Bajo",
    "medium": "Medio",
    "high": "Alto",
    "critical": "Crítico",
}


class Risk(db.Model):
    __tablename__ = "risks"

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessments.id"), nullable=False)
    code = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    asset = db.Column(db.String(200))
    threat = db.Column(db.String(200))
    vulnerability = db.Column(db.String(200))

    probability = db.Column(db.Integer, nullable=False)  # 1-5
    impact = db.Column(db.Integer, nullable=False)  # 1-5

    existing_controls = db.Column(db.Text)

    residual_probability = db.Column(db.Integer, nullable=True)
    residual_impact = db.Column(db.Integer, nullable=True)

    owner = db.Column(db.String(150))
    treatment = db.Column(db.String(20), default=TREATMENT_MITIGATE)
    target_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default=RISK_STATUS_OPEN)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    assessment = db.relationship("Assessment", back_populates="risks")
    actions = db.relationship("Action", back_populates="risk")

    @property
    def inherent_risk(self):
        return self.probability * self.impact

    @property
    def inherent_level(self):
        return risk_level(self.inherent_risk)

    @property
    def residual_risk(self):
        if self.residual_probability is None or self.residual_impact is None:
            return None
        return self.residual_probability * self.residual_impact

    @property
    def residual_level(self):
        return risk_level(self.residual_risk)

    def __repr__(self):
        return f"<Risk {self.code} {self.name}>"
