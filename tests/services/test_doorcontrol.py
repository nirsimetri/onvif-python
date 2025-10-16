import pytest
from onvif.services.doorcontrol import DoorControl


def test_doorcontrol_import():
    assert DoorControl is not None
