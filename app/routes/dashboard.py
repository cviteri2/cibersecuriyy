from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from app.models.organization import Organization
from app.models.assessment import Assessment
from app.services.report_data import build_assessment_report_data

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    if current_user.is_client():
        org = current_user.organization
        if not org:
            return render_template("dashboard/no_organization.html")
        assessment = (
            Assessment.query.filter_by(organization_id=org.id).order_by(Assessment.created_at.desc()).first()
        )
        if assessment:
            return redirect(url_for("dashboard.executive_dashboard", assessment_id=assessment.id))
        return redirect(url_for("organizations.detail", organization_id=org.id))

    organizations = Organization.query.order_by(Organization.legal_name).all()
    return render_template("dashboard/index.html", organizations=organizations)


@dashboard_bp.route("/assessments/<int:assessment_id>/dashboard")
@login_required
def executive_dashboard(assessment_id):
    from app.utils import get_assessment_or_403

    assessment = get_assessment_or_403(assessment_id)
    data = build_assessment_report_data(assessment)
    return render_template("dashboard/executive.html", **data)
