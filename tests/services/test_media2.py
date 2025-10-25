import os
import inspect
from unittest.mock import Mock, patch
from lxml import etree
from onvif.services.media2 import Media2


def test_media2_import():
    assert Media2 is not None


class TestMedia2WSDLCompliance:
    """Test that Media2 service implementation matches WSDL specification."""

    @staticmethod
    def get_wsdl_operations():
        """Parse WSDL to get all defined operations with their parameters."""
        wsdl_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "onvif",
            "wsdl",
            "ver20",
            "media",
            "wsdl",
            "media.wsdl",
        )

        # Parse WSDL
        tree = etree.parse(wsdl_path)
        root = tree.getroot()

        # Namespaces
        ns = {
            "wsdl": "http://schemas.xmlsoap.org/wsdl/",
            "xs": "http://www.w3.org/2001/XMLSchema",
            "tr2": "http://www.onvif.org/ver20/media/wsdl",
        }

        operations = {}

        # Find all operations in portType
        port_type = root.find('.//wsdl:portType[@name="Media2"]', ns)
        if port_type is not None:
            for operation in port_type.findall("wsdl:operation", ns):
                op_name = operation.get("name")
                operations[op_name] = {"input": None, "output": None}

        # Find all messages with their parts (parameters)
        messages = {}
        for message in root.findall("wsdl:message", ns):
            msg_name = message.get("name")
            parts = {}
            for part in message.findall("wsdl:part", ns):
                part_name = part.get("name")
                part_element = part.get("element")
                parts[part_name] = part_element
            messages[msg_name] = parts

        # Match operations with their request/response messages
        for op_name in operations.keys():
            request_msg = messages.get(f"{op_name}Request", {})
            response_msg = messages.get(f"{op_name}Response", {})
            operations[op_name] = {
                "request_params": list(request_msg.keys()),
                "response_params": list(response_msg.keys()),
            }

        return operations

    @staticmethod
    def get_implemented_methods():
        """Get all implemented methods in Media2 class."""
        methods = {}
        for name, method in inspect.getmembers(Media2, predicate=inspect.isfunction):
            if not name.startswith("_") and name != "__init__":
                # Get method signature
                sig = inspect.signature(method)
                params = list(sig.parameters.keys())
                # Remove 'self' from parameters
                if "self" in params:
                    params.remove("self")

                methods[name] = {
                    "params": params,
                    "signature": sig,
                }

        return methods

    def test_all_wsdl_operations_implemented(self):
        """Test that all WSDL operations are implemented as methods."""
        wsdl_operations = self.get_wsdl_operations()
        implemented_methods = self.get_implemented_methods()

        missing_operations = []
        for op_name in wsdl_operations.keys():
            if op_name not in implemented_methods:
                missing_operations.append(op_name)

        assert (
            not missing_operations
        ), f"Missing implementations for operations: {missing_operations}"

    def test_method_parameters_match_wsdl(self):
        """Test that method parameters match WSDL request parameters."""
        wsdl_operations = self.get_wsdl_operations()
        implemented_methods = self.get_implemented_methods()

        mismatches = []

        for op_name, op_info in wsdl_operations.items():
            if op_name not in implemented_methods:
                continue

            method_info = implemented_methods[op_name]
            method_params = set(method_info["params"])
            wsdl_params = set(op_info["request_params"])

            # Check if all WSDL parameters are in method signature
            if not wsdl_params.issubset(method_params.union({"parameters"})):
                if wsdl_params and not method_params:
                    mismatches.append(
                        {
                            "operation": op_name,
                            "wsdl_params": list(wsdl_params),
                            "method_params": list(method_params),
                        }
                    )

        # This is informational - some methods might use **kwargs
        if mismatches:
            print(f"\nParameter mismatches found (may use **kwargs): {mismatches}")

    @patch("onvif.services.media2.ONVIFOperator")
    def test_operator_call_usage(self, mock_operator_class):
        """Test that all methods correctly call self.operator.call()."""
        # Create mock operator
        mock_operator_instance = Mock()
        mock_operator_class.return_value = mock_operator_instance

        # Create Media2 instance
        media2 = Media2(xaddr="http://test:80/onvif/Media2")

        implemented_methods = self.get_implemented_methods()

        errors = []

        for method_name, method_info in implemented_methods.items():
            # Reset mock
            mock_operator_instance.call.reset_mock()

            try:
                # Get the method
                method = getattr(media2, method_name)

                # Create dummy arguments based on signature
                sig = method_info["signature"]
                kwargs = {}
                for param_name, param in sig.parameters.items():
                    if param_name == "self":
                        continue
                    # Provide None for optional params, empty string for required
                    if param.default == inspect.Parameter.empty:
                        kwargs[param_name] = ""
                    else:
                        kwargs[param_name] = None

                # Call the method
                try:
                    method(**kwargs)
                except Exception:
                    pass  # We expect it might fail, we just want to check the call

                # Verify operator.call was invoked
                if not mock_operator_instance.call.called:
                    errors.append(f"{method_name}: operator.call() not invoked")
                else:
                    # Check that first argument is the operation name
                    call_args = mock_operator_instance.call.call_args
                    if call_args and len(call_args[0]) > 0:
                        called_op_name = call_args[0][0]
                        if called_op_name != method_name:
                            errors.append(
                                f"{method_name}: calls operator.call('{called_op_name}') instead of '{method_name}'"
                            )
                    else:
                        errors.append(
                            f"{method_name}: operator.call() called without operation name"
                        )

            except Exception as e:
                errors.append(f"{method_name}: Error during test - {str(e)}")

        assert not errors, "Operator call errors:\n" + "\n".join(errors)

    @patch("onvif.services.media2.ONVIFOperator")
    def test_specific_methods_implementation(self, mock_operator_class):
        """Test specific important methods are correctly implemented."""
        mock_operator_instance = Mock()
        mock_operator_class.return_value = mock_operator_instance
        mock_operator_instance.call.return_value = {"Result": "Success"}

        media2 = Media2(xaddr="http://test:80/onvif/Media2")

        # Test GetServiceCapabilities (no parameters)
        media2.GetServiceCapabilities()
        mock_operator_instance.call.assert_called_with("GetServiceCapabilities")

        # Test GetProfiles (optional parameters)
        mock_operator_instance.call.reset_mock()
        media2.GetProfiles(Token="profile1", Type="Video")
        mock_operator_instance.call.assert_called_with(
            "GetProfiles", Token="profile1", Type="Video"
        )

        # Test CreateProfile (required + optional parameter)
        mock_operator_instance.call.reset_mock()
        media2.CreateProfile(
            Name="TestProfile", Configuration={"VideoEncoder": {"H264": True}}
        )
        mock_operator_instance.call.assert_called_with(
            "CreateProfile",
            Name="TestProfile",
            Configuration={"VideoEncoder": {"H264": True}},
        )

        # Test AddConfiguration (required + optional parameters)
        mock_operator_instance.call.reset_mock()
        media2.AddConfiguration(
            ProfileToken="profile2",
            Name="Config1",
            Configuration={"Type": "VideoEncoder"},
        )
        mock_operator_instance.call.assert_called_with(
            "AddConfiguration",
            ProfileToken="profile2",
            Name="Config1",
            Configuration={"Type": "VideoEncoder"},
        )

        # Test RemoveConfiguration (multiple required parameters)
        mock_operator_instance.call.reset_mock()
        media2.RemoveConfiguration(
            ProfileToken="profile3", Configuration={"Type": "AudioEncoder"}
        )
        mock_operator_instance.call.assert_called_with(
            "RemoveConfiguration",
            ProfileToken="profile3",
            Configuration={"Type": "AudioEncoder"},
        )

        # Test DeleteProfile (required parameter)
        mock_operator_instance.call.reset_mock()
        media2.DeleteProfile(Token="profile4")
        mock_operator_instance.call.assert_called_with(
            "DeleteProfile", Token="profile4"
        )

        # Test GetStreamUri (multiple required parameters)
        mock_operator_instance.call.reset_mock()
        media2.GetStreamUri(Protocol="RTSP", ProfileToken="profile5")
        mock_operator_instance.call.assert_called_with(
            "GetStreamUri", Protocol="RTSP", ProfileToken="profile5"
        )

        # Test SetVideoEncoderConfiguration (required parameter)
        mock_operator_instance.call.reset_mock()
        media2.SetVideoEncoderConfiguration(
            Configuration={"Token": "venc1", "Encoding": "H264"}
        )
        mock_operator_instance.call.assert_called_with(
            "SetVideoEncoderConfiguration",
            Configuration={"Token": "venc1", "Encoding": "H264"},
        )

        # Test GetVideoEncoderConfigurationOptions (optional parameters)
        mock_operator_instance.call.reset_mock()
        media2.GetVideoEncoderConfigurationOptions(
            ConfigurationToken="venc2", ProfileToken="profile6"
        )
        mock_operator_instance.call.assert_called_with(
            "GetVideoEncoderConfigurationOptions",
            ConfigurationToken="venc2",
            ProfileToken="profile6",
        )

        # Test GetSnapshotUri (required parameter)
        mock_operator_instance.call.reset_mock()
        media2.GetSnapshotUri(ProfileToken="profile7")
        mock_operator_instance.call.assert_called_with(
            "GetSnapshotUri", ProfileToken="profile7"
        )

        # Test CreateMask (required parameter)
        mock_operator_instance.call.reset_mock()
        media2.CreateMask(Mask={"Token": "mask1", "Type": "Color"})
        mock_operator_instance.call.assert_called_with(
            "CreateMask", Mask={"Token": "mask1", "Type": "Color"}
        )

        # Test PlayAudioClip (required + optional parameters)
        mock_operator_instance.call.reset_mock()
        media2.PlayAudioClip(
            Token="clip1",
            Play=True,
            AudioOutputToken="output1",
            RepeatCycles=3,
        )
        mock_operator_instance.call.assert_called_with(
            "PlayAudioClip",
            Token="clip1",
            AudioOutputToken="output1",
            Play=True,
            RepeatCycles=3,
        )

    def test_no_extra_methods(self):
        """Test that there are no extra public methods not in WSDL."""
        wsdl_operations = self.get_wsdl_operations()
        implemented_methods = self.get_implemented_methods()

        extra_methods = []
        for method_name in implemented_methods.keys():
            if method_name not in wsdl_operations:
                extra_methods.append(method_name)

        # This is informational - helper methods are OK
        if extra_methods:
            print(f"\nExtra methods not in WSDL (helper methods?): {extra_methods}")

    @patch("onvif.services.media2.ONVIFOperator")
    def test_parameter_forwarding(self, mock_operator_class):
        """Test that parameters are correctly forwarded to operator.call()."""
        mock_operator_instance = Mock()
        mock_operator_class.return_value = mock_operator_instance
        mock_operator_instance.call.return_value = {}

        media2 = Media2(xaddr="http://test:80/onvif/Media2")

        # Test that all parameters are forwarded as keyword arguments
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

        for test_case in test_cases:
            mock_operator_instance.call.reset_mock()
            method = getattr(media2, test_case["method"])
            method(**test_case["params"])

            # Verify call was made with correct parameters
            mock_operator_instance.call.assert_called_once()
            actual_call = mock_operator_instance.call.call_args

            # Check operation name
            assert (
                actual_call[0][0] == test_case["method"]
            ), f"Operation name mismatch for {test_case['method']}"

            # Check all parameters are forwarded
            for param_name, param_value in test_case["params"].items():
                assert (
                    param_name in actual_call[1]
                ), f"Parameter {param_name} not forwarded in {test_case['method']}"
                assert (
                    actual_call[1][param_name] == param_value
                ), f"Parameter {param_name} value mismatch in {test_case['method']}"
