from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db

ROLE_ADMIN = "admin"
ROLE_EVALUATOR = "evaluator"
ROLE_CLIENT = "client"
ROLES = [ROLE_ADMIN, ROLE_EVALUATOR, ROLE_CLIENT]


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"), nullable=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_CLIENT)
    is_active_flag = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    organization = db.relationship("Organization", back_populates="users")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return self.is_active_flag

    def is_admin(self):
        return self.role == ROLE_ADMIN

    def is_evaluator(self):
        return self.role == ROLE_EVALUATOR

    def is_client(self):
        return self.role == ROLE_CLIENT

    def can_access_organization(self, organization_id):
        if self.is_admin() or self.is_evaluator():
            return True
        return self.organization_id == organization_id

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
