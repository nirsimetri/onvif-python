import pytest
from onvif.services import media


def test_media_import():
    assert media is not None
