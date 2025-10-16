import pytest
from onvif.services.replay import Replay


def test_replay_import():
    assert Replay is not None
