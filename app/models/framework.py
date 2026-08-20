from app.extensions import db


class Framework(db.Model):
    __tablename__ = "frameworks"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)

    domains = db.relationship("Domain", back_populates="framework", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Framework {self.code}>"


class Domain(db.Model):
    __tablename__ = "domains"

    id = db.Column(db.Integer, primary_key=True)
    framework_id = db.Column(db.Integer, db.ForeignKey("frameworks.id"), nullable=False)
    code = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    order = db.Column(db.Integer, default=0)

    framework = db.relationship("Framework", back_populates="domains")
    questions = db.relationship("Question", back_populates="domain", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Domain {self.code} {self.name}>"
