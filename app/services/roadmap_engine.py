"""Roadmap engine: buckets action items into 90/180/365 day horizons and
orders them by a priority score combining risk severity, action priority
and target date proximity."""
from datetime import date

PRIORITY_WEIGHTS = {"critical": 40, "high": 30, "medium": 20, "low": 10}


def _priority_score(action):
    score = PRIORITY_WEIGHTS.get(action.priority, 15)
    if action.risk:
        score += action.risk.inherent_risk
    return score


def _horizon(action, today=None):
    today = today or date.today()
    if not action.target_date:
        return 365
    delta = (action.target_date - today).days
    if delta <= 90:
        return 90
    if delta <= 180:
        return 180
    return 365


def build_roadmap(actions, today=None):
    today = today or date.today()
    buckets = {90: [], 180: [], 365: []}
    for action in actions:
        buckets[_horizon(action, today)].append(action)

    for horizon in buckets:
        buckets[horizon] = sorted(buckets[horizon], key=lambda a: -_priority_score(a))

    return buckets
