import pytest
from onvif.services.media import Media


def test_media_import():
    assert Media is not None
