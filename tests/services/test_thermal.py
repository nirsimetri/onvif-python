import pytest
from onvif.services import thermal


def test_thermal_import():
    assert thermal is not None
