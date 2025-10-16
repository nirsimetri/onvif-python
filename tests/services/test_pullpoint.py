import pytest
from onvif.services.events.pullpoint import PullPoint


def test_pullpoint_import():
    assert PullPoint is not None