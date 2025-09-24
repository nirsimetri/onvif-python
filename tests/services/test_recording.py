import pytest
from onvif.services import recording


def test_recording_import():
    assert recording is not None
