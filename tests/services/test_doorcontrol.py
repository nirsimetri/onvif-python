import pytest
from onvif.services import doorcontrol


def test_doorcontrol_import():
    assert doorcontrol is not None
