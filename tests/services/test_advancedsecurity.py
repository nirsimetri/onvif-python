import pytest
from onvif.services.security import advancedsecurity


def test_advancedsecurity_import():
    assert advancedsecurity is not None
