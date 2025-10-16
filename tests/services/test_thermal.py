import pytest
from onvif.services.thermal import Thermal


def test_thermal_import():
    assert Thermal is not None
