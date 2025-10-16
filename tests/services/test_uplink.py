import pytest
from onvif.services.uplink import Uplink


def test_uplink_import():
    assert Uplink is not None
