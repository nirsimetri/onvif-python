import pytest
from onvif.services import devicemgmt


def test_devicemgmt_import():
    assert devicemgmt is not None
