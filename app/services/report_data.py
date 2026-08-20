"""Aggregates all computed results for an assessment: maturity, gap
analysis, risk summary and roadmap. Used by both the dashboard and the
PDF report so the numbers always match."""
from app.services.maturity_engine import compute_maturity
from app.services.compliance_engine import compute_gap_analysis
from app.services.risk_engine import compute_risk_summary, build_risk_matrix
from app.services.roadmap_engine import build_roadmap


def build_assessment_report_data(assessment):
    responses = list(assessment.responses)
    risks = list(assessment.risks)
    actions = list(assessment.actions)

    maturity = compute_maturity(responses)
    gap = compute_gap_analysis(responses)
    risk_summary = compute_risk_summary(risks)
    risk_matrix = build_risk_matrix(risks)
    roadmap = build_roadmap(actions)

    privacy_responses = [r for r in responses if r.question.domain.framework.code == "LOPDP"]
    privacy_gap = compute_gap_analysis(privacy_responses) if privacy_responses else None

    from datetime import date, timedelta

    today = date.today()
    open_actions = [a for a in actions if a.target_date and a.status not in ("completed", "cancelled")]
    overdue_actions = [a for a in open_actions if a.target_date < today]
    upcoming_actions = [
        a for a in open_actions if today <= a.target_date <= today + timedelta(days=30)
    ]

    pending_evidences = []
    for r in responses:
        for e in r.evidences:
            if e.status == "pending":
                pending_evidences.append(e)

    return {
        "assessment": assessment,
        "organization": assessment.organization,
        "responses": responses,
        "risks": risks,
        "actions": actions,
        "maturity": maturity,
        "gap": gap,
        "privacy_gap": privacy_gap,
        "risk_summary": risk_summary,
        "risk_matrix": risk_matrix,
        "roadmap": roadmap,
        "overdue_actions": overdue_actions,
        "upcoming_actions": upcoming_actions,
        "pending_evidences": pending_evidences,
        "total_questions": len(responses),
    }
