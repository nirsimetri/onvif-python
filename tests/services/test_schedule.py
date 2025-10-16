import pytest
from onvif.services.schedule import Schedule


def test_schedule_import():
    assert Schedule is not None
