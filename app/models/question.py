from app.extensions import db

ANSWER_YES = "yes"
ANSWER_PARTIAL = "partial"
ANSWER_NO = "no"
ANSWER_NA = "na"

ANSWER_SCORES = {
    ANSWER_YES: 5,
    ANSWER_PARTIAL: 2.5,
    ANSWER_NO: 0,
    ANSWER_NA: None,
}

ANSWER_LABELS = {
    ANSWER_YES: "Sí",
    ANSWER_PARTIAL: "Parcialmente",
    ANSWER_NO: "No",
    ANSWER_NA: "No aplica",
}


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    domain_id = db.Column(db.Integer, db.ForeignKey("domains.id"), nullable=False)
    code = db.Column(db.String(30), nullable=False)
    title = db.Column(db.String(400), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(120))
    weight = db.Column(db.Float, default=1.0)
    response_type = db.Column(db.String(20), default="choice")  # choice | numeric
    evidence_required = db.Column(db.Boolean, default=False)
    reference = db.Column(db.String(200))
    order = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)

    domain = db.relationship("Domain", back_populates="questions")
    responses = db.relationship("Response", back_populates="question")

    def __repr__(self):
        return f"<Question {self.code}>"
