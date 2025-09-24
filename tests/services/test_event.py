import pytest
from onvif.services.events import events


def test_event_import():
    assert events is not None
