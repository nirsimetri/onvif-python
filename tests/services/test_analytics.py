import pytest
from onvif.services.analytics import analytics


def test_analytics_import():
    assert analytics is not None
