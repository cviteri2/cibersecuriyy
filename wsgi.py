"""WSGI entry point for production deployment (PythonAnywhere).

On PythonAnywhere, point the "Source code" / WSGI configuration file to
import `application` from this module. See docs/PYTHONANYWHERE.md.
"""
import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.extensions import db

application = create_app(os.environ.get("FLASK_ENV", "production"))

with application.app_context():
    db.create_all()
