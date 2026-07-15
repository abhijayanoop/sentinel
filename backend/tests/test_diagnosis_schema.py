import pytest
from pydantic import ValidationError

from app.schemas.diagnosis import Diagnosis, RiskLevel


def test_confidence_must_be_in_range():
    with pytest.raises(ValidationError):
        Diagnosis(root_cause_hypothesis="x", confidence=1.5, risk_level=RiskLevel.low)


def test_valid_diagnosis_constructs():
    d = Diagnosis(root_cause_hypothesis="memory leak after deploy", confidence=0.8, risk_level=RiskLevel.high)
    assert d.suggested_action is None
    assert d.risk_level == RiskLevel.high