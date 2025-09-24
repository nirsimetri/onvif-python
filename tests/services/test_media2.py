import pytest
from onvif.services import media2


def test_media2_import():
    assert media2 is not None
