from app.services.maturity_engine import compute_maturity, maturity_label
from app.services.compliance_engine import compute_gap_analysis
from app.models.question import ANSWER_YES, ANSWER_PARTIAL, ANSWER_NO, ANSWER_NA, ANSWER_SCORES


class FakeFramework:
    def __init__(self, name):
        self.name = name
        self.code = name


class FakeDomain:
    def __init__(self, name, framework):
        self.name = name
        self.framework = framework


class FakeQuestion:
    def __init__(self, domain, weight=1.0, category="General"):
        self.domain = domain
        self.weight = weight
        self.category = category


class FakeResponse:
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer
        self.score = ANSWER_SCORES[answer]


def _build_responses():
    fw = FakeFramework("ISO27001")
    domain = FakeDomain("Gobierno", fw)
    q1 = FakeQuestion(domain, weight=1.0)
    q2 = FakeQuestion(domain, weight=1.0)
    q3 = FakeQuestion(domain, weight=1.0)
    q4 = FakeQuestion(domain, weight=1.0)
    return [
        FakeResponse(q1, ANSWER_YES),
        FakeResponse(q2, ANSWER_PARTIAL),
        FakeResponse(q3, ANSWER_NO),
        FakeResponse(q4, ANSWER_NA),
    ]


def test_maturity_label_boundaries():
    assert maturity_label(0) == "Inexistente"
    assert maturity_label(5) == "Optimizado"
    assert maturity_label(None) == "Sin datos"


def test_compute_maturity_excludes_na_and_weights_correctly():
    responses = _build_responses()
    result = compute_maturity(responses)
    # yes=5, partial=2.5, no=0 -> average of applicable (na excluded) = (5+2.5+0)/3
    assert result["global"] == round((5 + 2.5 + 0) / 3, 2)
    assert "Gobierno" in result["by_domain"]
    assert "ISO27001" in result["by_framework"]


def test_compute_maturity_empty_returns_none():
    result = compute_maturity([])
    assert result["global"] is None


def test_compute_gap_analysis_percentages():
    responses = _build_responses()
    gap = compute_gap_analysis(responses)
    # applicable = 3 (yes, partial, no); compliant=1, partial=1 -> (1 + 0.5)/3*100
    assert gap["overall_percent"] == round((1 + 0.5) / 3 * 100, 1)
    assert gap["totals"]["applicable"] == 3
    assert gap["totals"]["compliant"] == 1
    assert gap["totals"]["partial"] == 1
    assert gap["totals"]["non_compliant"] == 1


def test_compute_gap_analysis_identifies_critical_gaps():
    fw = FakeFramework("ISO27002")
    domain = FakeDomain("Tecnológicos", fw)
    heavy_question = FakeQuestion(domain, weight=2.0)
    light_question = FakeQuestion(domain, weight=1.0)
    responses = [
        FakeResponse(heavy_question, ANSWER_NO),
        FakeResponse(light_question, ANSWER_PARTIAL),
    ]
    gap = compute_gap_analysis(responses)
    assert len(gap["critical_gaps"]) == 1
    assert len(gap["high_priority_gaps"]) == 1


def test_compute_gap_analysis_all_na_returns_none():
    fw = FakeFramework("LOPDP")
    domain = FakeDomain("Privacidad", fw)
    q = FakeQuestion(domain)
    gap = compute_gap_analysis([FakeResponse(q, ANSWER_NA)])
    assert gap["overall_percent"] is None
