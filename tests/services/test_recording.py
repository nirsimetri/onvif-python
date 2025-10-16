import pytest
from onvif.services.recording import Recording


def test_recording_import():
    assert Recording is not None
