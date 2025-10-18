from onvif.services.security.mediasigning import MediaSigning


def test_mediasigning_import():
    assert MediaSigning is not None
