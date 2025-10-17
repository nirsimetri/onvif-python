import pytest
from onvif.services.analytics.ruleengine import RuleEngine


def test_ruleengine_import():
    assert RuleEngine is not None
