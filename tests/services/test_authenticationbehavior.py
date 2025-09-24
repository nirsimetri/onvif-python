import pytest
from onvif.services import authenticationbehavior


def test_authenticationbehavior_import():
    assert authenticationbehavior is not None
