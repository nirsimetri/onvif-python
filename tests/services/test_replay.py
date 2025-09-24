import pytest
from onvif.services import replay


def test_replay_import():
    assert replay is not None
