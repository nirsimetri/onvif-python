import pytest
from onvif.services.analyticsdevice import AnalyticsDevice


def test_analyticsdevice_import():
    assert AnalyticsDevice is not None