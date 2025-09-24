import pytest
from onvif.services import appmgmt


def test_appmgmt_import():
    assert appmgmt is not None
