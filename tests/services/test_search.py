import pytest
from onvif.services import search


def test_search_import():
    assert search is not None
