import pytest
from onvif.services import provisioning


def test_provisioning_import():
    assert provisioning is not None
