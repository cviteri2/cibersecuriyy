from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.forms import OrganizationForm
from app.models.organization import Organization
from app.models.assessment import Assessment
from app.utils import staff_required, get_organization_or_403
from app.services.audit_service import log_action

organizations_bp = Blueprint("organizations", __name__, url_prefix="/organizations")


@organizations_bp.route("/")
@login_required
@staff_required
def list_organizations():
    organizations = Organization.query.order_by(Organization.legal_name).all()
    return render_template("organizations/list.html", organizations=organizations)


@organizations_bp.route("/new", methods=["GET", "POST"])
@login_required
@staff_required
def create():
    form = OrganizationForm()
    if form.validate_on_submit():
        org = Organization()
        form.populate_obj(org)
        db.session.add(org)
        db.session.commit()
        log_action("create", entity="organization", entity_id=org.id, detail=org.legal_name)
        flash("Organización creada correctamente.", "success")
        return redirect(url_for("organizations.detail", organization_id=org.id))
    return render_template("organizations/form.html", form=form, title="Nueva organización")


@organizations_bp.route("/<int:organization_id>")
@login_required
def detail(organization_id):
    org = get_organization_or_403(organization_id)
    assessments = (
        Assessment.query.filter_by(organization_id=org.id).order_by(Assessment.created_at.desc()).all()
    )
    return render_template("organizations/detail.html", organization=org, assessments=assessments)


@organizations_bp.route("/<int:organization_id>/edit", methods=["GET", "POST"])
@login_required
@staff_required
def edit(organization_id):
    org = get_organization_or_403(organization_id)
    form = OrganizationForm(obj=org)
    if form.validate_on_submit():
        form.populate_obj(org)
        db.session.commit()
        log_action("update", entity="organization", entity_id=org.id, detail=org.legal_name)
        flash("Organización actualizada correctamente.", "success")
        return redirect(url_for("organizations.detail", organization_id=org.id))
    return render_template("organizations/form.html", form=form, title="Editar organización", organization=org)
