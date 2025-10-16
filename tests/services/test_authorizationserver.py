import pytest
from onvif.services.security.authorizationserver import AuthorizationServer


def test_authorizationserver_import():
    assert AuthorizationServer is not None