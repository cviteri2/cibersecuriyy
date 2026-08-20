"""Maturity scoring engine.

Maturity scale (0-5): matches the raw answer score scale so results map
directly onto the maturity levels defined for the platform:

0 Inexistente, 1 Inicial, 2 En desarrollo, 3 Definido, 4 Gestionado, 5 Optimizado
"""
from app.models.question import ANSWER_NA

MATURITY_LEVELS = {
    0: "Inexistente",
    1: "Inicial",
    2: "En desarrollo",
    3: "Definido",
    4: "Gestionado",
    5: "Optimizado",
}


def maturity_label(score):
    if score is None:
        return "Sin datos"
    return MATURITY_LEVELS.get(round(score), MATURITY_LEVELS[5] if score > 5 else MATURITY_LEVELS[0])


def _weighted_average(responses):
    total_weight = 0.0
    total_score = 0.0
    for r in responses:
        if r.answer == ANSWER_NA or r.score is None:
            continue
        weight = r.question.weight or 1.0
        total_weight += weight
        total_score += r.score * weight
    if total_weight == 0:
        return None
    return round(total_score / total_weight, 2)


def compute_maturity(responses):
    """Compute global, per-domain, per-framework and per-category maturity.

    Returns a dict with:
      global: float|None
      by_domain: {domain_name: {"score": float, "framework": str}}
      by_framework: {framework_name: float}
      by_category: {category: float}
    """
    global_score = _weighted_average(responses)

    by_domain_responses = {}
    by_framework_responses = {}
    by_category_responses = {}

    for r in responses:
        domain = r.question.domain
        framework = domain.framework
        category = r.question.category or "General"

        by_domain_responses.setdefault(domain.name, []).append(r)
        by_framework_responses.setdefault(framework.name, []).append(r)
        by_category_responses.setdefault(category, []).append(r)

    by_domain = {
        name: _weighted_average(items) for name, items in by_domain_responses.items()
    }
    by_framework = {
        name: _weighted_average(items) for name, items in by_framework_responses.items()
    }
    by_category = {
        name: _weighted_average(items) for name, items in by_category_responses.items()
    }

    return {
        "global": global_score,
        "global_label": maturity_label(global_score),
        "by_domain": by_domain,
        "by_framework": by_framework,
        "by_category": by_category,
    }
