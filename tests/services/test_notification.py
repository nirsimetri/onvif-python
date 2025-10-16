import pytest
from onvif.services.events.notification import Notification


def test_notification_import():
    assert Notification is not None