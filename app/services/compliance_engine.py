"""Gap analysis / compliance engine.

Compliance = (compliant + 0.5 * partial) / applicable
"""
from app.models.question import ANSWER_YES, ANSWER_PARTIAL, ANSWER_NO, ANSWER_NA


def _classify(responses):
    applicable = [r for r in responses if r.answer != ANSWER_NA]
    compliant = [r for r in applicable if r.answer == ANSWER_YES]
    partial = [r for r in applicable if r.answer == ANSWER_PARTIAL]
    non_compliant = [r for r in applicable if r.answer == ANSWER_NO]
    return applicable, compliant, partial, non_compliant


def _compliance_percent(responses):
    applicable, compliant, partial, non_compliant = _classify(responses)
    if not applicable:
        return None
    score = (len(compliant) + 0.5 * len(partial)) / len(applicable) * 100
    return round(score, 1)


def compute_gap_analysis(responses):
    """Returns overall + per-domain + per-framework compliance percentages
    and lists of critical / high priority gaps."""

    overall = _compliance_percent(responses)

    by_domain_responses = {}
    by_framework_responses = {}
    for r in responses:
        domain = r.question.domain
        framework = domain.framework
        by_domain_responses.setdefault(domain.name, []).append(r)
        by_framework_responses.setdefault(framework.name, []).append(r)

    by_domain = {name: _compliance_percent(items) for name, items in by_domain_responses.items()}
    by_framework = {
        name: _compliance_percent(items) for name, items in by_framework_responses.items()
    }

    gaps = [r for r in responses if r.answer in (ANSWER_NO, ANSWER_PARTIAL)]
    critical_gaps = sorted(
        [g for g in gaps if g.answer == ANSWER_NO and (g.question.weight or 1.0) >= 1.5],
        key=lambda r: -(r.question.weight or 1.0),
    )
    high_priority_gaps = sorted(
        [g for g in gaps if g not in critical_gaps],
        key=lambda r: -(r.question.weight or 1.0),
    )

    applicable, compliant, partial, non_compliant = _classify(responses)

    return {
        "overall_percent": overall,
        "by_domain": by_domain,
        "by_framework": by_framework,
        "critical_gaps": critical_gaps,
        "high_priority_gaps": high_priority_gaps,
        "totals": {
            "applicable": len(applicable),
            "compliant": len(compliant),
            "partial": len(partial),
            "non_compliant": len(non_compliant),
        },
    }
