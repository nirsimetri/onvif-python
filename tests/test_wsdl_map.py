import os
import pytest
from onvif import ONVIFWSDL


def test_get_wsdl_definition_valid():
    """Test valid WSDL definition retrieval"""
    definition = ONVIFWSDL.get_definition("devicemgmt", "ver10")

    assert isinstance(definition, dict)
    assert "path" in definition
    assert "binding" in definition
    assert "namespace" in definition
    assert os.path.exists(
        definition["path"]
    ), f"WSDL path not found: {definition['path']}"


def test_get_wsdl_definition_invalid_service():
    """Test invalid service name"""
    with pytest.raises(ValueError) as excinfo:
        ONVIFWSDL.get_definition("invalid_service", "ver10")
    assert "Unknown service" in str(excinfo.value)


def test_get_wsdl_definition_invalid_version():
    """Test invalid version for existing service"""
    with pytest.raises(ValueError) as excinfo:
        ONVIFWSDL.get_definition("devicemgmt", "ver99")
    assert "not available" in str(excinfo.value)


@pytest.mark.parametrize("service", ["devicemgmt", "media"])
@pytest.mark.parametrize("version", ["ver10"])
def test_get_wsdl_definition_combinations(service, version):
    """Test various service and version combinations"""
    definition = ONVIFWSDL.get_definition(service, version)

    assert isinstance(definition, dict)
    assert "path" in definition
    assert os.path.exists(
        definition["path"]
    ), f"{service} {version} missing: {definition['path']}"

    # Verify binding and namespace are present
    assert definition["binding"] is not None
    assert definition["namespace"] is not None
