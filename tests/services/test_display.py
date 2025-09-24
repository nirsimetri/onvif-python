import pytest
from onvif.services import display


def test_display_import():
    assert display is not None
