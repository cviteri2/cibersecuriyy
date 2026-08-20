import os
import uuid
from datetime import datetime, timezone

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.extensions import db
from app.forms import AssessmentForm, ResponseForm, EvidenceForm
from app.models.organization import Organization
from app.models.assessment import Assessment, STATUS_IN_PROGRESS, STATUS_COMPLETED
from app.models.framework import Framework, Domain
from app.models.question import Question, ANSWER_SCORES
from app.models.response import Response
from app.models.evidence import Evidence, STATUS_RECEIVED
from app.utils import staff_required, get_organization_or_403, get_assessment_or_403
from app.services.audit_service import log_action
from app.services.report_data import build_assessment_report_data

assessment_bp = Blueprint("assessment", __name__)


@assessment_bp.route("/organizations/<int:organization_id>/assessments/new", methods=["GET", "POST"])
@login_required
@staff_required
def create(organization_id):
    org = get_organization_or_403(organization_id)
    form = AssessmentForm()
    if form.validate_on_submit():
        assessment = Assessment(
            organization_id=org.id,
            name=form.name.data,
            evaluator_id=current_user.id,
            status=STATUS_IN_PROGRESS,
        )
        db.session.add(assessment)
        db.session.commit()
        log_action("create", entity="assessment", entity_id=assessment.id, detail=assessment.name)
        flash("Evaluación creada correctamente.", "success")
        return redirect(url_for("assessment.questionnaire_overview", assessment_id=assessment.id))
    return render_template("assessment/form.html", form=form, organization=org)


@assessment_bp.route("/assessments/<int:assessment_id>")
@login_required
def detail(assessment_id):
    assessment = get_assessment_or_403(assessment_id)
    data = build_assessment_report_data(assessment)
    return render_template("dashboard/executive.html", **data)


@assessment_bp.route("/assessments/<int:assessment_id>/questionnaire")
@login_required
def questionnaire_overview(assessment_id):
    assessment = get_assessment_or_403(assessment_id)
    frameworks = Framework.query.order_by(Framework.order).all()
    total_questions = Question.query.filter_by(active=True).count()
    answered_ids = {r.question_id for r in assessment.responses}

    domain_progress = []
    for fw in frameworks:
        for domain in fw.domains:
            total = len(domain.questions)
            answered = sum(1 for q in domain.questions if q.id in answered_ids)
            domain_progress.append(
                {
                    "domain": domain,
                    "framework": fw,
                    "total": total,
                    "answered": answered,
                    "percent": round(answered / total * 100, 0) if total else 0,
                }
            )

    return render_template(
        "assessment/questionnaire_overview.html",
        assessment=assessment,
        domain_progress=domain_progress,
        overall_progress=assessment.progress_percent(total_questions),
        total_questions=total_questions,
        answered_questions=len(answered_ids),
    )


@assessment_bp.route("/assessments/<int:assessment_id>/questionnaire/<int:domain_id>", methods=["GET"])
@login_required
def questionnaire_domain(assessment_id, domain_id):
    assessment = get_assessment_or_403(assessment_id)
    domain = Domain.query.get_or_404(domain_id)
    responses_by_question = {r.question_id: r for r in assessment.responses if r.question.domain_id == domain_id}
    questions = sorted(domain.questions, key=lambda q: q.order)
    return render_template(
        "assessment/questionnaire_domain.html",
        assessment=assessment,
        domain=domain,
        questions=questions,
        responses_by_question=responses_by_question,
    )


@assessment_bp.route(
    "/assessments/<int:assessment_id>/questionnaire/<int:domain_id>/answer/<int:question_id>",
    methods=["POST"],
)
@login_required
def answer_question(assessment_id, domain_id, question_id):
    assessment = get_assessment_or_403(assessment_id)
    question = Question.query.get_or_404(question_id)
    form = ResponseForm()

    if form.validate_on_submit():
        response = Response.query.filter_by(assessment_id=assessment.id, question_id=question.id).first()
        if not response:
            response = Response(assessment_id=assessment.id, question_id=question.id)
            db.session.add(response)
        response.answer = form.answer.data
        response.score = ANSWER_SCORES.get(form.answer.data)
        response.notes = form.notes.data
        db.session.commit()
        log_action("answer_question", entity="response", entity_id=response.id, detail=question.code)
        flash(f"Respuesta guardada para {question.code}.", "success")
    else:
        flash("No se pudo guardar la respuesta.", "danger")

    return redirect(url_for("assessment.questionnaire_domain", assessment_id=assessment.id, domain_id=domain_id))


def _allowed_file(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_EVIDENCE_EXTENSIONS"]


@assessment_bp.route("/responses/<int:response_id>/evidence", methods=["POST"])
@login_required
def upload_evidence(response_id):
    response = Response.query.get_or_404(response_id)
    assessment = get_assessment_or_403(response.assessment_id)
    form = EvidenceForm()

    if not form.validate_on_submit():
        flash("No se pudo registrar la evidencia.", "danger")
        return redirect(
            url_for(
                "assessment.questionnaire_domain",
                assessment_id=assessment.id,
                domain_id=response.question.domain_id,
            )
        )

    file_path = None
    file_type = None
    file = form.file.data
    if file and file.filename:
        if not _allowed_file(file.filename):
            flash("Tipo de archivo no permitido.", "danger")
            return redirect(
                url_for(
                    "assessment.questionnaire_domain",
                    assessment_id=assessment.id,
                    domain_id=response.question.domain_id,
                )
            )
        ext = file.filename.rsplit(".", 1)[-1].lower()
        file_type = ext
        stored_name = f"{uuid.uuid4().hex}.{ext}"
        safe_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], f"assessment_{assessment.id}")
        os.makedirs(safe_dir, exist_ok=True)
        file.save(os.path.join(safe_dir, stored_name))
        file_path = os.path.join(f"assessment_{assessment.id}", stored_name)

    evidence = Evidence(
        response_id=response.id,
        name=form.name.data,
        description=form.description.data,
        responsible=form.responsible.data,
        file_type=file_type,
        file_path=file_path,
        status=STATUS_RECEIVED if file_path else "pending",
        uploaded_by_id=current_user.id,
    )
    db.session.add(evidence)
    db.session.commit()
    log_action("upload_evidence", entity="evidence", entity_id=evidence.id, detail=evidence.name)
    flash("Evidencia registrada correctamente.", "success")
    return redirect(
        url_for(
            "assessment.questionnaire_domain",
            assessment_id=assessment.id,
            domain_id=response.question.domain_id,
        )
    )


@assessment_bp.route("/evidence/<int:evidence_id>/download")
@login_required
def download_evidence(evidence_id):
    evidence = Evidence.query.get_or_404(evidence_id)
    assessment = get_assessment_or_403(evidence.response.assessment_id)
    if not evidence.file_path:
        abort(404)
    directory = current_app.config["UPLOAD_FOLDER"]
    return send_from_directory(directory, evidence.file_path, as_attachment=True)


@assessment_bp.route("/assessments/<int:assessment_id>/complete", methods=["POST"])
@login_required
@staff_required
def complete(assessment_id):
    assessment = get_assessment_or_403(assessment_id)
    assessment.status = STATUS_COMPLETED
    assessment.completed_at = datetime.now(timezone.utc)
    db.session.commit()
    log_action("complete_assessment", entity="assessment", entity_id=assessment.id)
    flash("Evaluación marcada como completada.", "success")
    return redirect(url_for("dashboard.executive_dashboard", assessment_id=assessment.id))
