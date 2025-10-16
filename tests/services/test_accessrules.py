import pytest
from onvif.services.accessrules import AccessRules


def test_accessrules_import():
    assert AccessRules is not None