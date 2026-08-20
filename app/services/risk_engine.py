"""Risk assessment engine: probability x impact scoring and matrix."""
from app.models.risk import risk_level, RISK_LEVEL_LABELS


def compute_risk_summary(risks):
    critical = [r for r in risks if r.inherent_level == "critical"]
    high = [r for r in risks if r.inherent_level == "high"]
    medium = [r for r in risks if r.inherent_level == "medium"]
    low = [r for r in risks if r.inherent_level == "low"]

    top_risks = sorted(risks, key=lambda r: -r.inherent_risk)[:10]

    return {
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low,
        "top_risks": top_risks,
        "counts": {
            "critical": len(critical),
            "high": len(high),
            "medium": len(medium),
            "low": len(low),
            "total": len(risks),
        },
    }


def build_risk_matrix(risks):
    """5x5 matrix: matrix[impact][probability] = list of risks.
    impact rows go 5 (top) to 1 (bottom); probability columns 1..5."""
    matrix = {impact: {prob: [] for prob in range(1, 6)} for impact in range(1, 6)}
    for r in risks:
        if 1 <= r.probability <= 5 and 1 <= r.impact <= 5:
            matrix[r.impact][r.probability].append(r)
    return matrix


def cell_level(probability, impact):
    return risk_level(probability * impact)
