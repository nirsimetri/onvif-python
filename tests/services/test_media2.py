from onvif.services import Media2
from base_service_test import ONVIFServiceTestBase


class TestMedia2WSDLCompliance(ONVIFServiceTestBase):
    """Test that Media2 service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = Media2
    SERVICE_NAME = "media2"
    WSDL_PATH_COMPONENTS = ["ver20", "media", "wsdl", "media.wsdl"]
    BINDING_NAME = "Media2Binding"
    NAMESPACE_PREFIX = "tr2"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver20/media/wsdl"
    XADDR_PATH = "/onvif/Media2"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetServiceCapabilities", "params": {}},
            {
                "method": "GetProfiles",
                "params": {"Token": "profile1", "Type": "Video"},
            },
            {
                "method": "CreateProfile",
                "params": {
                    "Name": "TestProfile",
                    "Configuration": {"VideoEncoder": {"H264": True}},
                },
            },
            {
                "method": "AddConfiguration",
                "params": {
                    "ProfileToken": "profile2",
                    "Name": "Config1",
                    "Configuration": {"Type": "VideoEncoder"},
                },
            },
            {
                "method": "RemoveConfiguration",
                "params": {
                    "ProfileToken": "profile3",
                    "Configuration": {"Type": "AudioEncoder"},
                },
            },
            {"method": "DeleteProfile", "params": {"Token": "profile4"}},
            {
                "method": "GetStreamUri",
                "params": {"Protocol": "RTSP", "ProfileToken": "profile5"},
            },
            {
                "method": "SetVideoEncoderConfiguration",
                "params": {"Configuration": {"Token": "venc1", "Encoding": "H264"}},
            },
            {
                "method": "GetVideoEncoderConfigurationOptions",
                "params": {
                    "ConfigurationToken": "venc2",
                    "ProfileToken": "profile6",
                },
            },
            {"method": "GetSnapshotUri", "params": {"ProfileToken": "profile7"}},
            {
                "method": "CreateMask",
                "params": {"Mask": {"Token": "mask1", "Type": "Color"}},
            },
            {
                "method": "PlayAudioClip",
                "params": {
                    "Token": "clip1",
                    "Play": True,
                    "AudioOutputToken": "output1",
                    "RepeatCycles": 3,
                },
            },
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "GetProfiles",
                "params": {"Token": "prof1", "Type": "Audio"},
            },
            {
                "method": "CreateProfile",
                "params": {
                    "Name": "NewProfile",
                    "Configuration": {"AudioEncoder": True},
                },
            },
            {
                "method": "AddConfiguration",
                "params": {
                    "ProfileToken": "prof2",
                    "Name": "NewConfig",
                    "Configuration": {"Type": "Metadata"},
                },
            },
            {
                "method": "RemoveConfiguration",
                "params": {
                    "ProfileToken": "prof3",
                    "Configuration": {"Type": "VideoSource"},
                },
            },
            {
                "method": "DeleteProfile",
                "params": {"Token": "prof4"},
            },
            {
                "method": "GetStreamUri",
                "params": {"Protocol": "HTTP", "ProfileToken": "prof5"},
            },
            {
                "method": "SetVideoEncoderConfiguration",
                "params": {"Configuration": {"Token": "venc1", "Quality": 5}},
            },
            {
                "method": "GetVideoEncoderConfigurationOptions",
                "params": {"ConfigurationToken": "venc2", "ProfileToken": "prof6"},
            },
            {
                "method": "GetSnapshotUri",
                "params": {"ProfileToken": "prof7"},
            },
            {
                "method": "SetVideoSourceMode",
                "params": {
                    "VideoSourceToken": "vs1",
                    "VideoSourceModeToken": "mode1",
                },
            },
            {
                "method": "GetOSDs",
                "params": {"OSDToken": "osd1", "ConfigurationToken": "config1"},
            },
            {
                "method": "SetOSD",
                "params": {
                    "OSD": {"Token": "osd2", "VideoSourceConfigurationToken": "vs2"}
                },
            },
            {
                "method": "CreateMask",
                "params": {
                    "Mask": {"Token": "mask1", "VideoSourceConfigurationToken": "vs3"}
                },
            },
            {
                "method": "DeleteMask",
                "params": {"Token": "mask2"},
            },
            {
                "method": "PlayAudioClip",
                "params": {
                    "Token": "clip1",
                    "Play": False,
                    "AudioOutputToken": "output1",
                    "RepeatCycles": 5,
                },
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
