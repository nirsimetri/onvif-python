from onvif.services.security.jwt import JWT


def test_jwt_import():
    assert JWT is not None
