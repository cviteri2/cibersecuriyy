from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required

from app.extensions import db
from app.forms import RiskForm
from app.models.risk import Risk
from app.utils import staff_required, get_assessment_or_403
from app.services.audit_service import log_action
from app.services.risk_engine import compute_risk_summary, build_risk_matrix

risks_bp = Blueprint("risks", __name__, url_prefix="/assessments/<int:assessment_id>/risks")


@risks_bp.route("/")
@login_required
def list_risks(assessment_id):
    assessment = get_assessment_or_403(assessment_id)
    summary = compute_risk_summary(assessment.risks)
    return render_template("risks/list.html", assessment=assessment, risks=assessment.risks, summary=summary)


@risks_bp.route("/matrix")
@login_required
def matrix(assessment_id):
    assessment = get_assessment_or_403(assessment_id)
    matrix = build_risk_matrix(assessment.risks)
    return render_template("risks/matrix.html", assessment=assessment, matrix=matrix)


@risks_bp.route("/new", methods=["GET", "POST"])
@login_required
@staff_required
def create(assessment_id):
    assessment = get_assessment_or_403(assessment_id)
    form = RiskForm()
    if form.validate_on_submit():
        risk = Risk(assessment_id=assessment.id)
        _populate_risk(risk, form)
        db.session.add(risk)
        db.session.commit()
        log_action("create", entity="risk", entity_id=risk.id, detail=risk.name)
        flash("Riesgo registrado correctamente.", "success")
        return redirect(url_for("risks.list_risks", assessment_id=assessment.id))
    return render_template("risks/form.html", form=form, assessment=assessment, title="Nuevo riesgo")


@risks_bp.route("/<int:risk_id>/edit", methods=["GET", "POST"])
@login_required
@staff_required
def edit(assessment_id, risk_id):
    assessment = get_assessment_or_403(assessment_id)
    risk = Risk.query.filter_by(id=risk_id, assessment_id=assessment.id).first_or_404()
    form = RiskForm(obj=risk)
    if form.validate_on_submit():
        _populate_risk(risk, form)
        db.session.commit()
        log_action("update", entity="risk", entity_id=risk.id, detail=risk.name)
        flash("Riesgo actualizado correctamente.", "success")
        return redirect(url_for("risks.list_risks", assessment_id=assessment.id))
    return render_template("risks/form.html", form=form, assessment=assessment, risk=risk, title="Editar riesgo")


@risks_bp.route("/<int:risk_id>/delete", methods=["POST"])
@login_required
@staff_required
def delete(assessment_id, risk_id):
    assessment = get_assessment_or_403(assessment_id)
    risk = Risk.query.filter_by(id=risk_id, assessment_id=assessment.id).first_or_404()
    db.session.delete(risk)
    db.session.commit()
    log_action("delete", entity="risk", entity_id=risk_id, detail=risk.name)
    flash("Riesgo eliminado.", "info")
    return redirect(url_for("risks.list_risks", assessment_id=assessment.id))


def _populate_risk(risk, form):
    risk.code = form.code.data
    risk.name = form.name.data
    risk.description = form.description.data
    risk.asset = form.asset.data
    risk.threat = form.threat.data
    risk.vulnerability = form.vulnerability.data
    risk.probability = form.probability.data
    risk.impact = form.impact.data
    risk.existing_controls = form.existing_controls.data
    risk.residual_probability = int(form.residual_probability.data) if form.residual_probability.data else None
    risk.residual_impact = int(form.residual_impact.data) if form.residual_impact.data else None
    risk.owner = form.owner.data
    risk.treatment = form.treatment.data
    risk.target_date = form.target_date.data
    risk.status = form.status.data
