import pytest
from onvif.services import ptz


def test_ptz_import():
    assert ptz is not None
