import pytest
from onvif.services.security.keystore import Keystore


def test_keystore_import():
    assert Keystore is not None