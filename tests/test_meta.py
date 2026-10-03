"""Tests for the onvif.meta module."""

from typing import Final, get_type_hints

from onvif import meta


def test_version():
    """Test that the __version__ attribute is a non-empty string with two dots."""
    assert isinstance(meta.__version__, str)
    assert meta.__version__
    assert meta.__version__.count(".") == 2


def test_repository():
    """Test that the __repository__ attribute is a non-empty string with a valid URL."""
    assert meta.__repository__ == "https://github.com/nirsimetri/onvif-python"


def test_metadata_annotations():
    """Test that the __version__ and __repository__ attributes have the correct type
    annotations."""
    annotations = get_type_hints(meta)

    assert annotations["__version__"] is Final[str]
    assert annotations["__repository__"] is Final[str]
