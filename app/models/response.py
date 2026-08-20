from datetime import datetime, timezone
from app.extensions import db


class Response(db.Model):
    __tablename__ = "responses"
    __table_args__ = (db.UniqueConstraint("assessment_id", "question_id", name="uq_assessment_question"),)

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessments.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    answer = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text)
    updated_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    assessment = db.relationship("Assessment", back_populates="responses")
    question = db.relationship("Question", back_populates="responses")
    evidences = db.relationship("Evidence", back_populates="response", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Response q={self.question_id} a={self.answer}>"
