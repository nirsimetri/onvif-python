import pytest
from onvif.services.imaging import Imaging


def test_imaging_import():
    assert Imaging is not None
