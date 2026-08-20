import os
import logging

from flask import Flask, render_template, request

from config import config_by_name
from app.extensions import db, login_manager, csrf


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "production")

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_by_name.get(config_name, config_by_name["production"]))

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Por favor inicia sesión para continuar."
    login_manager.login_message_category = "warning"
    csrf.init_app(app)

    if not app.debug:
        logging.basicConfig(level=logging.INFO)

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.organizations import organizations_bp
    from app.routes.assessment import assessment_bp
    from app.routes.risks import risks_bp
    from app.routes.actions import actions_bp
    from app.routes.reports import reports_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(organizations_bp)
    app.register_blueprint(assessment_bp)
    app.register_blueprint(risks_bp)
    app.register_blueprint(actions_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(admin_bp)

    register_error_handlers(app)
    register_security_headers(app)

    @app.context_processor
    def inject_globals():
        from app.models.question import ANSWER_LABELS
        from app.models.risk import RISK_LEVEL_LABELS, TREATMENT_LABELS, RISK_STATUS_LABELS
        from app.models.action import PRIORITY_LABELS, ACTION_STATUS_LABELS
        from app.models.assessment import STATUS_LABELS

        return dict(
            ANSWER_LABELS=ANSWER_LABELS,
            RISK_LEVEL_LABELS=RISK_LEVEL_LABELS,
            TREATMENT_LABELS=TREATMENT_LABELS,
            RISK_STATUS_LABELS=RISK_STATUS_LABELS,
            PRIORITY_LABELS=PRIORITY_LABELS,
            ACTION_STATUS_LABELS=ACTION_STATUS_LABELS,
            ASSESSMENT_STATUS_LABELS=STATUS_LABELS,
        )

    return app


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template("errors/400.html"), 400

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.exception("Internal server error")
        return render_template("errors/500.html"), 500


def register_security_headers(app):
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if request.is_secure:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response
