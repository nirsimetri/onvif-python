import pytest
from onvif.services import credential


def test_credential_import():
    assert credential is not None
