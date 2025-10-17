import pytest
from onvif.services.security.tlsserver import TLSServer


def test_tlsserver_import():
    assert TLSServer is not None
