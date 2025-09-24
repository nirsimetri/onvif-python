import os
import pytest
from onvif import ONVIFWSDL


def test_get_wsdl_path_valid():
    path = ONVIFWSDL.get_definition("device", "ver20")
    assert os.path.exists(path), f"WSDL path not found: {path}"


def test_get_wsdl_path_invalid_service():
    with pytest.raises(ValueError) as excinfo:
        ONVIFWSDL.get_definition("invalid_service", "ver20")
    assert "Unknown service" in str(excinfo.value)


def test_get_wsdl_path_invalid_version():
    with pytest.raises(ValueError) as excinfo:
        ONVIFWSDL.get_definition("device", "ver99")
    assert "not available" in str(excinfo.value)


@pytest.mark.parametrize("service", ["device", "media"])
@pytest.mark.parametrize("version", ["ver10", "ver20"])
def test_get_wsdl_path_all_combinations(service, version):
    path = ONVIFWSDL.get_definition(service, version)
    assert os.path.exists(path), f"{service} {version} missing: {path}"
