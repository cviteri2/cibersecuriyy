from datetime import date, timedelta

from app.models.risk import Risk, risk_level
from app.models.action import Action, PRIORITY_HIGH, PRIORITY_CRITICAL
from app.services.risk_engine import compute_risk_summary, build_risk_matrix
from app.services.roadmap_engine import build_roadmap


def make_risk(probability, impact, residual_probability=None, residual_impact=None):
    return Risk(
        code="RSK-X",
        name="Riesgo",
        probability=probability,
        impact=impact,
        residual_probability=residual_probability,
        residual_impact=residual_impact,
    )


def test_risk_level_classification():
    assert risk_level(1) == "low"
    assert risk_level(4) == "low"
    assert risk_level(5) == "medium"
    assert risk_level(9) == "medium"
    assert risk_level(10) == "high"
    assert risk_level(16) == "high"
    assert risk_level(17) == "critical"
    assert risk_level(25) == "critical"


def test_inherent_risk_calculation():
    risk = make_risk(4, 5)
    assert risk.inherent_risk == 20
    assert risk.inherent_level == "critical"


def test_residual_risk_calculation():
    risk = make_risk(4, 5, residual_probability=2, residual_impact=3)
    assert risk.residual_risk == 6
    assert risk.residual_level == "medium"


def test_residual_risk_none_when_not_set():
    risk = make_risk(3, 3)
    assert risk.residual_risk is None
    assert risk.residual_level is None


def test_compute_risk_summary_counts():
    risks = [make_risk(5, 5), make_risk(4, 4), make_risk(3, 3), make_risk(1, 1)]
    summary = compute_risk_summary(risks)
    assert summary["counts"]["critical"] == 1
    assert summary["counts"]["high"] == 1
    assert summary["counts"]["medium"] == 1
    assert summary["counts"]["low"] == 1
    assert summary["counts"]["total"] == 4
    assert summary["top_risks"][0].inherent_risk == 25


def test_build_risk_matrix_places_risks_in_correct_cell():
    r = make_risk(3, 4)
    matrix = build_risk_matrix([r])
    assert r in matrix[4][3]
    assert matrix[4][3] == [r]


def test_build_roadmap_buckets_by_target_date():
    today = date.today()
    a90 = Action(title="A90", priority=PRIORITY_CRITICAL, target_date=today + timedelta(days=30))
    a180 = Action(title="A180", priority=PRIORITY_HIGH, target_date=today + timedelta(days=150))
    a365 = Action(title="A365", priority=PRIORITY_HIGH, target_date=today + timedelta(days=300))
    a_none = Action(title="ANone", priority=PRIORITY_HIGH, target_date=None)

    roadmap = build_roadmap([a90, a180, a365, a_none], today=today)
    assert a90 in roadmap[90]
    assert a180 in roadmap[180]
    assert a365 in roadmap[365]
    assert a_none in roadmap[365]


def test_build_roadmap_orders_by_priority_and_risk():
    today = date.today()
    high_risk = make_risk(5, 5)
    low_action = Action(title="Low", priority="low", target_date=today + timedelta(days=10))
    critical_action = Action(title="Critical", priority=PRIORITY_CRITICAL, target_date=today + timedelta(days=10), risk=high_risk)

    roadmap = build_roadmap([low_action, critical_action], today=today)
    assert roadmap[90][0] is critical_action
