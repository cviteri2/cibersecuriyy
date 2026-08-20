from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required

from app.extensions import db
from app.forms import ActionForm
from app.models.action import Action
from app.utils import staff_required, get_assessment_or_403
from app.services.audit_service import log_action
from app.services.roadmap_engine import build_roadmap

actions_bp = Blueprint("actions", __name__, url_prefix="/assessments/<int:assessment_id>/actions")


def _load_form_choices(form, assessment):
    form.risk_id.choices = [(0, "— Ninguno —")] + [(r.id, f"{r.code} - {r.name}") for r in assessment.risks]


@actions_bp.route("/")
@login_required
def list_actions(assessment_id):
    assessment = get_assessment_or_403(assessment_id)
    roadmap = build_roadmap(assessment.actions)
    return render_template("actions/list.html", assessment=assessment, actions=assessment.actions, roadmap=roadmap)


@actions_bp.route("/new", methods=["GET", "POST"])
@login_required
@staff_required
def create(assessment_id):
    assessment = get_assessment_or_403(assessment_id)
    form = ActionForm()
    _load_form_choices(form, assessment)
    if form.validate_on_submit():
        action = Action(assessment_id=assessment.id)
        _populate_action(action, form)
        db.session.add(action)
        db.session.commit()
        log_action("create", entity="action", entity_id=action.id, detail=action.title)
        flash("Acción registrada correctamente.", "success")
        return redirect(url_for("actions.list_actions", assessment_id=assessment.id))
    return render_template("actions/form.html", form=form, assessment=assessment, title="Nueva acción")


@actions_bp.route("/<int:action_id>/edit", methods=["GET", "POST"])
@login_required
@staff_required
def edit(assessment_id, action_id):
    assessment = get_assessment_or_403(assessment_id)
    action = Action.query.filter_by(id=action_id, assessment_id=assessment.id).first_or_404()
    form = ActionForm(obj=action)
    _load_form_choices(form, assessment)
    if not form.is_submitted():
        form.risk_id.data = action.risk_id or 0
    if form.validate_on_submit():
        _populate_action(action, form)
        db.session.commit()
        log_action("update", entity="action", entity_id=action.id, detail=action.title)
        flash("Acción actualizada correctamente.", "success")
        return redirect(url_for("actions.list_actions", assessment_id=assessment.id))
    return render_template("actions/form.html", form=form, assessment=assessment, action=action, title="Editar acción")


def _populate_action(action, form):
    action.title = form.title.data
    action.description = form.description.data
    action.risk_id = form.risk_id.data if form.risk_id.data else None
    action.control_ref = form.control_ref.data
    action.responsible = form.responsible.data
    action.priority = form.priority.data
    action.start_date = form.start_date.data
    action.target_date = form.target_date.data
    action.status = form.status.data
    action.progress = form.progress.data or 0
    action.closure_evidence = form.closure_evidence.data
