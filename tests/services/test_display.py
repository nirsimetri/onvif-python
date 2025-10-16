import pytest
from onvif.services.display import Display


def test_display_import():
    assert Display is not None
