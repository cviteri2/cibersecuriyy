import os
import tempfile

import pytest

from app import create_app
from app.extensions import db as _db
from app.seed import seed_question_bank, seed_demo_data


@pytest.fixture()
def app():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    test_app = create_app("testing")
    test_app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.session.remove()
        _db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def seeded(app):
    with app.app_context():
        seed_question_bank()
        seed_demo_data("DemoPass123!")
    return app


def login(client, email, password="DemoPass123!"):
    return client.post("/login", data={"email": email, "password": password}, follow_redirects=True)
