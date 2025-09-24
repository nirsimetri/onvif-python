import pytest
from onvif.services import deviceio


def test_deviceio_import():
    assert deviceio is not None
