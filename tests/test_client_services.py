"""Tests for the ONVIFClient services initialization."""

import pytest

from onvif.services import (
    JWT,
    PTZ,
    AccessControl,
    AccessRules,
    ActionEngine,
    AdvancedSecurity,
    Analytics,
    AnalyticsDevice,
    AppManagement,
    AuthenticationBehavior,
    AuthorizationServer,
    Credential,
    DeviceIO,
    Display,
    DoorControl,
    Dot1X,
    Events,
    Imaging,
    Keystore,
    Media,
    Media2,
    MediaSigning,
    Notification,
    Provisioning,
    Receiver,
    Recording,
    Replay,
    RuleEngine,
    Schedule,
    Search,
    Thermal,
    TLSServer,
    Uplink,
)


@pytest.mark.parametrize(
    ("method_name", "private_name", "service_class", "service_path"),
    [
        ("events", "_events", Events, "Events"),
        ("notification", "_notification", Notification, "Notification"),
        ("imaging", "_imaging", Imaging, "Imaging"),
        ("media", "_media", Media, "Media"),
        ("media2", "_media2", Media2, "Media2"),
        ("ptz", "_ptz", PTZ, "PTZ"),
        ("deviceio", "_deviceio", DeviceIO, "DeviceIO"),
        ("display", "_display", Display, "Display"),
        ("analytics", "_analytics", Analytics, "Analytics"),
        ("ruleengine", "_ruleengine", RuleEngine, "RuleEngine"),
        ("analyticsdevice", "_analyticsdevice", AnalyticsDevice, "AnalyticsDevice"),
        ("accesscontrol", "_accesscontrol", AccessControl, "AccessControl"),
        ("doorcontrol", "_doorcontrol", DoorControl, "DoorControl"),
        ("accessrules", "_accessrules", AccessRules, "AccessRules"),
        ("actionengine", "_actionengine", ActionEngine, "ActionEngine"),
        ("appmanagement", "_appmanagement", AppManagement, "AppManagement"),
        (
            "authenticationbehavior",
            "_authenticationbehavior",
            AuthenticationBehavior,
            "AuthenticationBehavior",
        ),
        ("credential", "_credential", Credential, "Credential"),
        ("recording", "_recording", Recording, "Recording"),
        ("replay", "_replay", Replay, "Replay"),
        ("provisioning", "_provisioning", Provisioning, "Provisioning"),
        ("receiver", "_receiver", Receiver, "Receiver"),
        ("schedule", "_schedule", Schedule, "Schedule"),
        ("search", "_search", Search, "Search"),
        ("thermal", "_thermal", Thermal, "Thermal"),
        ("uplink", "_uplink", Uplink, "Uplink"),
        ("security", "_security", AdvancedSecurity, "Security"),
        ("jwt", "_jwt", JWT, "JWT"),
        ("keystore", "_keystore", Keystore, "Keystore"),
        ("tlsserver", "_tlsserver", TLSServer, "TLSServer"),
        ("dot1x", "_dot1x", Dot1X, "Dot1X"),
        (
            "authorizationserver",
            "_authorizationserver",
            AuthorizationServer,
            "AuthorizationServer",
        ),
        ("mediasigning", "_mediasigning", MediaSigning, "MediaSigning"),
    ],
)
def test_lazy_service_initialization(
    mock_onvif_client,
    monkeypatch,
    method_name,
    private_name,
    service_class,
    service_path,
):
    """Test lazy initialization and caching of ONVIF services."""
    client = mock_onvif_client

    xaddr = f"http://192.168.1.17:8000/onvif/{service_path}"

    monkeypatch.setattr(
        client,
        "_get_xaddr",
        lambda service, name: xaddr,
    )

    # Service has not been initialized yet.
    setattr(client, private_name, None)

    # Call the service accessor to trigger lazy initialization.
    service = getattr(client, method_name)()

    assert isinstance(service, service_class)
    # pylint: disable=protected-access
    assert client._get_xaddr(method_name, service_path) == xaddr
    assert getattr(client, private_name) is service

    # Calling the accessor again must return the cached instance.
    assert getattr(client, method_name)() is service
