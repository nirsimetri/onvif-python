import pytest
from onvif.services import imaging


def test_imaging_import():
    assert imaging is not None
