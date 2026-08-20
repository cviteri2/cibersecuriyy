"""Database seed script.

Creates the reference question bank (ISO 27001, ISO 27002, LOPDP) plus a
demo organization, users and a fully answered demo assessment (with
evidences, risks and actions) so the platform can be evaluated end to end.

Usage: flask --app run.py seed
"""
from datetime import date, timedelta

from app.extensions import db
from app.data.seed_questions import FRAMEWORKS
from app.models.user import User, ROLE_ADMIN, ROLE_EVALUATOR, ROLE_CLIENT
from app.models.organization import Organization
from app.models.framework import Framework, Domain
from app.models.question import Question, ANSWER_YES, ANSWER_PARTIAL, ANSWER_NO, ANSWER_SCORES
from app.models.assessment import Assessment, STATUS_IN_PROGRESS
from app.models.response import Response
from app.models.evidence import Evidence, STATUS_VALIDATED, STATUS_PENDING
from app.models.risk import Risk, TREATMENT_MITIGATE, TREATMENT_ACCEPT, RISK_STATUS_OPEN, RISK_STATUS_IN_TREATMENT
from app.models.action import Action, PRIORITY_HIGH, PRIORITY_CRITICAL, PRIORITY_MEDIUM, ACTION_STATUS_IN_PROGRESS, ACTION_STATUS_PENDING


def seed_question_bank():
    if Framework.query.first():
        return
    for fw_data in FRAMEWORKS:
        framework = Framework(code=fw_data["code"], name=fw_data["name"], description=fw_data["description"])
        db.session.add(framework)
        db.session.flush()
        for order_d, domain_data in enumerate(fw_data["domains"]):
            domain = Domain(framework_id=framework.id, code=domain_data["code"], name=domain_data["name"], order=order_d)
            db.session.add(domain)
            db.session.flush()
            for order_q, q in enumerate(domain_data["questions"]):
                question = Question(
                    domain_id=domain.id,
                    code=q["code"],
                    title=q["title"],
                    description=q.get("description", ""),
                    category=q.get("category", "General"),
                    weight=q.get("weight", 1.0),
                    evidence_required=q.get("evidence_required", False),
                    reference=q.get("reference", ""),
                    order=order_q,
                )
                db.session.add(question)
    db.session.commit()


def seed_demo_data(admin_password):
    if Organization.query.filter_by(legal_name="Empresa Demo S.A.").first():
        return

    org = Organization(
        legal_name="Empresa Demo S.A.",
        trade_name="Demo Corp",
        tax_id="1790000000001",
        sector="Servicios financieros",
        employee_count=150,
        country="Ecuador",
        city="Quito",
        contact_name="María Pérez",
        contact_email="contacto@demo-corp.ec",
        contact_phone="+593 99 000 0000",
        evaluation_date=date.today(),
        responsible_evaluator="Equipo de Consultoría",
    )
    db.session.add(org)
    db.session.flush()

    admin = User(name="Administrador", email="admin@demo-corp.ec", role=ROLE_ADMIN)
    admin.set_password(admin_password)

    evaluator = User(name="Evaluador Demo", email="evaluador@demo-corp.ec", role=ROLE_EVALUATOR)
    evaluator.set_password(admin_password)

    client = User(name="Cliente Demo", email="cliente@demo-corp.ec", role=ROLE_CLIENT, organization_id=org.id)
    client.set_password(admin_password)

    db.session.add_all([admin, evaluator, client])
    db.session.flush()

    assessment = Assessment(
        organization_id=org.id,
        name="Evaluación 2026 - Diagnóstico Inicial",
        evaluator_id=evaluator.id,
        status=STATUS_IN_PROGRESS,
    )
    db.session.add(assessment)
    db.session.flush()

    questions = Question.query.all()
    import random

    random.seed(42)
    answer_cycle = [ANSWER_YES, ANSWER_YES, ANSWER_PARTIAL, ANSWER_NO, ANSWER_YES, ANSWER_PARTIAL]
    for i, question in enumerate(questions):
        answer = answer_cycle[i % len(answer_cycle)]
        response = Response(
            assessment_id=assessment.id,
            question_id=question.id,
            answer=answer,
            score=ANSWER_SCORES[answer],
            notes="Respuesta de demostración generada automáticamente.",
        )
        db.session.add(response)
        db.session.flush()

        if question.evidence_required and answer != ANSWER_NO:
            evidence = Evidence(
                response_id=response.id,
                name=f"Evidencia - {question.code}",
                description="Documento de referencia asociado a la respuesta.",
                file_type="pdf",
                responsible="Equipo interno de seguridad",
                status=STATUS_VALIDATED if answer == ANSWER_YES else STATUS_PENDING,
            )
            db.session.add(evidence)

    risks_data = [
        dict(code="RSK-001", name="Falta de autenticación multifactor en accesos remotos",
             asset="VPN corporativa", threat="Acceso no autorizado", vulnerability="Ausencia de MFA",
             probability=4, impact=5, treatment=TREATMENT_MITIGATE, status=RISK_STATUS_IN_TREATMENT,
             residual_probability=2, residual_impact=4, owner="Jefe de TI"),
        dict(code="RSK-002", name="Copias de seguridad no probadas periódicamente",
             asset="Servidores de base de datos", threat="Pérdida de información", vulnerability="Backups sin pruebas de restauración",
             probability=3, impact=5, treatment=TREATMENT_MITIGATE, status=RISK_STATUS_OPEN,
             owner="Administrador de infraestructura"),
        dict(code="RSK-003", name="Ausencia de cifrado en medios de almacenamiento móviles",
             asset="Laptops y USB corporativos", threat="Fuga de información", vulnerability="Discos sin cifrar",
             probability=3, impact=4, treatment=TREATMENT_MITIGATE, status=RISK_STATUS_OPEN,
             owner="Jefe de TI"),
        dict(code="RSK-004", name="Personal sin capacitación reciente en seguridad",
             asset="Colaboradores", threat="Ingeniería social / phishing", vulnerability="Falta de concienciación",
             probability=4, impact=3, treatment=TREATMENT_MITIGATE, status=RISK_STATUS_OPEN,
             owner="Recursos Humanos"),
        dict(code="RSK-005", name="Proveedores sin cláusulas de protección de datos",
             asset="Contratos con terceros", threat="Incumplimiento normativo LOPDP", vulnerability="Contratos sin cláusulas de encargo de tratamiento",
             probability=3, impact=3, treatment=TREATMENT_ACCEPT, status=RISK_STATUS_OPEN,
             owner="Legal"),
    ]
    risks = []
    for rd in risks_data:
        risk = Risk(assessment_id=assessment.id, **rd)
        db.session.add(risk)
        risks.append(risk)
    db.session.flush()

    actions_data = [
        dict(title="Implementar MFA en accesos remotos", risk=risks[0], priority=PRIORITY_CRITICAL,
             status=ACTION_STATUS_IN_PROGRESS, progress=40, days_target=45, responsible="Jefe de TI",
             control_ref="ORG-5.15 / TEC-8.5"),
        dict(title="Definir y ejecutar plan de pruebas de restauración de backups", risk=risks[1], priority=PRIORITY_HIGH,
             status=ACTION_STATUS_PENDING, progress=0, days_target=75, responsible="Administrador de infraestructura",
             control_ref="TEC-8.13"),
        dict(title="Desplegar cifrado de disco en equipos móviles", risk=risks[2], priority=PRIORITY_HIGH,
             status=ACTION_STATUS_PENDING, progress=0, days_target=150, responsible="Jefe de TI",
             control_ref="TEC-8.24"),
        dict(title="Ejecutar campaña de concienciación en seguridad", risk=risks[3], priority=PRIORITY_MEDIUM,
             status=ACTION_STATUS_PENDING, progress=0, days_target=120, responsible="Recursos Humanos",
             control_ref="PER-6.3"),
        dict(title="Actualizar contratos con cláusulas de encargo de tratamiento", risk=risks[4], priority=PRIORITY_MEDIUM,
             status=ACTION_STATUS_PENDING, progress=0, days_target=300, responsible="Legal",
             control_ref="LOPDP-11"),
    ]
    for ad in actions_data:
        action = Action(
            assessment_id=assessment.id,
            risk_id=ad["risk"].id,
            title=ad["title"],
            description=f"Acción de tratamiento para el riesgo {ad['risk'].code}: {ad['risk'].name}.",
            control_ref=ad["control_ref"],
            responsible=ad["responsible"],
            priority=ad["priority"],
            start_date=date.today(),
            target_date=date.today() + timedelta(days=ad["days_target"]),
            status=ad["status"],
            progress=ad["progress"],
        )
        db.session.add(action)

    db.session.commit()


def run_seed(admin_password="ChangeMe123!"):
    seed_question_bank()
    seed_demo_data(admin_password)
