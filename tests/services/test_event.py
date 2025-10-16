import pytest
from onvif.services.events.events import Events


def test_events_import():
    assert Events is not None
