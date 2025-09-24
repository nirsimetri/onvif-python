import pytest
from onvif.services import uplink


def test_uplink_import():
    assert uplink is not None
