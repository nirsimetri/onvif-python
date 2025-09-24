import pytest
from onvif.services import receiver


def test_receiver_import():
    assert receiver is not None
