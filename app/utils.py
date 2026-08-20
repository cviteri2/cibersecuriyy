from functools import wraps
from flask import abort
from flask_login import current_user

from app.models.organization import Organization
from app.models.assessment import Assessment


def roles_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            if current_user.role not in roles:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


def staff_required(view):
    """Admin or evaluator only."""
    return roles_required("admin", "evaluator")(view)


def admin_required(view):
    return roles_required("admin")(view)


def get_organization_or_403(organization_id):
    org = Organization.query.get_or_404(organization_id)
    if not current_user.can_access_organization(org.id):
        abort(403)
    return org


def get_assessment_or_403(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    if not current_user.can_access_organization(assessment.organization_id):
        abort(403)
    return assessment
