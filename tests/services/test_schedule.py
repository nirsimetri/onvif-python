import pytest
from onvif.services import schedule


def test_schedule_import():
    assert schedule is not None
