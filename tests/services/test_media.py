from onvif.services import Media
from base_service_test import ONVIFServiceTestBase


class TestMediaWSDLCompliance(ONVIFServiceTestBase):
    """Test that Media service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = Media
    SERVICE_NAME = "media"
    WSDL_PATH_COMPONENTS = ["ver10", "media", "wsdl", "media.wsdl"]
    BINDING_NAME = "MediaBinding"
    NAMESPACE_PREFIX = "trt"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/media/wsdl"
    XADDR_PATH = "/onvif/Media"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetServiceCapabilities"},
            {"method": "GetProfiles"},
            {"method": "GetProfile", "params": {"ProfileToken": "profile1"}},
            {
                "method": "CreateProfile",
                "params": {"Name": "TestProfile", "Token": "token1"},
            },
            {
                "method": "GetStreamUri",
                "params": {
                    "StreamSetup": {
                        "Stream": "RTP-Unicast",
                        "Transport": {"Protocol": "RTSP"},
                    },
                    "ProfileToken": "profile2",
                },
            },
            {"method": "GetSnapshotUri", "params": {"ProfileToken": "profile3"}},
            {
                "method": "AddVideoEncoderConfiguration",
                "params": {"ProfileToken": "profile4", "ConfigurationToken": "config1"},
            },
            {
                "method": "SetVideoEncoderConfiguration",
                "params": {
                    "Configuration": {"Token": "config2", "Encoding": "H264"},
                    "ForcePersistence": True,
                },
            },
            {
                "method": "GetVideoEncoderConfigurationOptions",
                "params": {"ConfigurationToken": "config3", "ProfileToken": "profile5"},
            },
            {"method": "DeleteProfile", "params": {"ProfileToken": "profile6"}},
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {"method": "GetProfile", "params": {"ProfileToken": "prof1"}},
            {
                "method": "CreateProfile",
                "params": {"Name": "NewProfile", "Token": "newtoken"},
            },
            {
                "method": "GetStreamUri",
                "params": {
                    "StreamSetup": {"Stream": "RTP-Multicast"},
                    "ProfileToken": "prof2",
                },
            },
            {"method": "GetSnapshotUri", "params": {"ProfileToken": "prof3"}},
            {
                "method": "AddVideoEncoderConfiguration",
                "params": {"ProfileToken": "prof4", "ConfigurationToken": "venc1"},
            },
            {
                "method": "SetVideoEncoderConfiguration",
                "params": {
                    "Configuration": {"Token": "venc2", "Quality": 5},
                    "ForcePersistence": False,
                },
            },
            {
                "method": "GetVideoEncoderConfigurationOptions",
                "params": {"ConfigurationToken": "venc3", "ProfileToken": "prof5"},
            },
            {"method": "DeleteProfile", "params": {"ProfileToken": "prof6"}},
            {
                "method": "GetVideoSourceConfiguration",
                "params": {"ConfigurationToken": "vsrc1"},
            },
            {
                "method": "SetVideoSourceConfiguration",
                "params": {
                    "Configuration": {"Token": "vsrc2"},
                    "ForcePersistence": True,
                },
            },
            {
                "method": "AddPTZConfiguration",
                "params": {"ProfileToken": "prof7", "ConfigurationToken": "ptz1"},
            },
            {"method": "RemovePTZConfiguration", "params": {"ProfileToken": "prof8"}},
            {"method": "GetVideoSourceModes", "params": {"VideoSourceToken": "vs1"}},
            {
                "method": "SetVideoSourceMode",
                "params": {
                    "VideoSourceToken": "vs2",
                    "VideoSourceModeToken": "mode1",
                },
            },
            {"method": "GetOSD", "params": {"OSDToken": "osd1"}},
            {
                "method": "SetOSD",
                "params": {
                    "OSD": {"Token": "osd2", "TextString": {"PlainText": "Test"}}
                },
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
