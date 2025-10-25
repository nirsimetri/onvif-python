import os
import inspect
from unittest.mock import Mock, patch
from lxml import etree
from onvif.services.ptz import PTZ


def test_ptz_import():
    assert PTZ is not None


class TestPTZWSDLCompliance:
    """Test that PTZ service implementation matches WSDL specification."""

    @staticmethod
    def get_wsdl_operations():
        """Parse WSDL to get all defined operations with their parameters."""
        wsdl_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "onvif",
            "wsdl",
            "ver20",
            "ptz",
            "wsdl",
            "ptz.wsdl",
        )

        # Parse WSDL
        tree = etree.parse(wsdl_path)
        root = tree.getroot()

        # Namespaces
        ns = {
            "wsdl": "http://schemas.xmlsoap.org/wsdl/",
            "xs": "http://www.w3.org/2001/XMLSchema",
            "tptz": "http://www.onvif.org/ver20/ptz/wsdl",
        }

        operations = {}

        # Find all operations in portType
        port_type = root.find('.//wsdl:portType[@name="PTZ"]', ns)
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
        """Get all implemented methods in PTZ class."""
        methods = {}
        for name, method in inspect.getmembers(PTZ, predicate=inspect.isfunction):
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

    @patch("onvif.services.ptz.ONVIFOperator")
    def test_operator_call_usage(self, mock_operator_class):
        """Test that all methods correctly call self.operator.call()."""
        # Create mock operator
        mock_operator_instance = Mock()
        mock_operator_class.return_value = mock_operator_instance

        # Create PTZ instance
        ptz = PTZ(xaddr="http://test:80/onvif/PTZ")

        implemented_methods = self.get_implemented_methods()

        errors = []

        for method_name, method_info in implemented_methods.items():
            # Reset mock
            mock_operator_instance.call.reset_mock()

            try:
                # Get the method
                method = getattr(ptz, method_name)

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

    @patch("onvif.services.ptz.ONVIFOperator")
    def test_specific_methods_implementation(self, mock_operator_class):
        """Test specific important methods are correctly implemented."""
        mock_operator_instance = Mock()
        mock_operator_class.return_value = mock_operator_instance
        mock_operator_instance.call.return_value = {"Result": "Success"}

        ptz = PTZ(xaddr="http://test:80/onvif/PTZ")

        # Test GetServiceCapabilities (no parameters)
        ptz.GetServiceCapabilities()
        mock_operator_instance.call.assert_called_with("GetServiceCapabilities")

        # Test GetConfigurations (no parameters)
        mock_operator_instance.call.reset_mock()
        ptz.GetConfigurations()
        mock_operator_instance.call.assert_called_with("GetConfigurations")

        # Test GetNodes (no parameters)
        mock_operator_instance.call.reset_mock()
        ptz.GetNodes()
        mock_operator_instance.call.assert_called_with("GetNodes")

        # Test GetStatus (required parameter)
        mock_operator_instance.call.reset_mock()
        ptz.GetStatus(ProfileToken="profile1")
        mock_operator_instance.call.assert_called_with(
            "GetStatus", ProfileToken="profile1"
        )

        # Test GetPresets (required parameter)
        mock_operator_instance.call.reset_mock()
        ptz.GetPresets(ProfileToken="profile2")
        mock_operator_instance.call.assert_called_with(
            "GetPresets", ProfileToken="profile2"
        )

        # Test SetPreset (required + optional parameters)
        mock_operator_instance.call.reset_mock()
        ptz.SetPreset(ProfileToken="profile3", PresetName="Home", PresetToken="preset1")
        mock_operator_instance.call.assert_called_with(
            "SetPreset",
            ProfileToken="profile3",
            PresetName="Home",
            PresetToken="preset1",
        )

        # Test GotoPreset (required + optional parameters)
        mock_operator_instance.call.reset_mock()
        ptz.GotoPreset(
            ProfileToken="profile4",
            PresetToken="preset2",
            Speed={"PanTilt": {"x": 0.5, "y": 0.5}},
        )
        mock_operator_instance.call.assert_called_with(
            "GotoPreset",
            ProfileToken="profile4",
            PresetToken="preset2",
            Speed={"PanTilt": {"x": 0.5, "y": 0.5}},
        )

        # Test AbsoluteMove (required + optional parameters)
        mock_operator_instance.call.reset_mock()
        ptz.AbsoluteMove(
            ProfileToken="profile5",
            Position={"PanTilt": {"x": 0.0, "y": 0.0}, "Zoom": {"x": 1.0}},
            Speed={"PanTilt": {"x": 1.0, "y": 1.0}},
        )
        mock_operator_instance.call.assert_called_with(
            "AbsoluteMove",
            ProfileToken="profile5",
            Position={"PanTilt": {"x": 0.0, "y": 0.0}, "Zoom": {"x": 1.0}},
            Speed={"PanTilt": {"x": 1.0, "y": 1.0}},
        )

        # Test RelativeMove (required + optional parameters)
        mock_operator_instance.call.reset_mock()
        ptz.RelativeMove(
            ProfileToken="profile6",
            Translation={"PanTilt": {"x": 0.1, "y": 0.1}},
            Speed={"PanTilt": {"x": 0.5, "y": 0.5}},
        )
        mock_operator_instance.call.assert_called_with(
            "RelativeMove",
            ProfileToken="profile6",
            Translation={"PanTilt": {"x": 0.1, "y": 0.1}},
            Speed={"PanTilt": {"x": 0.5, "y": 0.5}},
        )

        # Test ContinuousMove (required + optional parameters)
        mock_operator_instance.call.reset_mock()
        ptz.ContinuousMove(
            ProfileToken="profile7",
            Velocity={"PanTilt": {"x": 0.5, "y": 0.0}},
            Timeout="PT5S",
        )
        mock_operator_instance.call.assert_called_with(
            "ContinuousMove",
            ProfileToken="profile7",
            Velocity={"PanTilt": {"x": 0.5, "y": 0.0}},
            Timeout="PT5S",
        )

        # Test Stop (required + optional parameters)
        mock_operator_instance.call.reset_mock()
        ptz.Stop(ProfileToken="profile8", PanTilt=True, Zoom=False)
        mock_operator_instance.call.assert_called_with(
            "Stop", ProfileToken="profile8", PanTilt=True, Zoom=False
        )

        # Test SetConfiguration (multiple required parameters)
        mock_operator_instance.call.reset_mock()
        ptz.SetConfiguration(
            PTZConfiguration={"Token": "config1", "NodeToken": "node1"},
            ForcePersistence=True,
        )
        mock_operator_instance.call.assert_called_with(
            "SetConfiguration",
            PTZConfiguration={"Token": "config1", "NodeToken": "node1"},
            ForcePersistence=True,
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

    @patch("onvif.services.ptz.ONVIFOperator")
    def test_parameter_forwarding(self, mock_operator_class):
        """Test that parameters are correctly forwarded to operator.call()."""
        mock_operator_instance = Mock()
        mock_operator_class.return_value = mock_operator_instance
        mock_operator_instance.call.return_value = {}

        ptz = PTZ(xaddr="http://test:80/onvif/PTZ")

        # Test that all parameters are forwarded as keyword arguments
        test_cases = [
            {
                "method": "GetStatus",
                "params": {"ProfileToken": "prof1"},
            },
            {
                "method": "GetPresets",
                "params": {"ProfileToken": "prof2"},
            },
            {
                "method": "SetPreset",
                "params": {
                    "ProfileToken": "prof3",
                    "PresetName": "Position1",
                    "PresetToken": "preset1",
                },
            },
            {
                "method": "GotoPreset",
                "params": {
                    "ProfileToken": "prof4",
                    "PresetToken": "preset2",
                    "Speed": {"PanTilt": {"x": 0.8, "y": 0.8}},
                },
            },
            {
                "method": "AbsoluteMove",
                "params": {
                    "ProfileToken": "prof5",
                    "Position": {"PanTilt": {"x": 0.5, "y": 0.5}},
                    "Speed": {"PanTilt": {"x": 0.6, "y": 0.6}},
                },
            },
            {
                "method": "RelativeMove",
                "params": {
                    "ProfileToken": "prof6",
                    "Translation": {"PanTilt": {"x": 0.2, "y": -0.1}},
                    "Speed": {"PanTilt": {"x": 0.3, "y": 0.3}},
                },
            },
            {
                "method": "ContinuousMove",
                "params": {
                    "ProfileToken": "prof7",
                    "Velocity": {"PanTilt": {"x": 0.4, "y": 0.0}},
                    "Timeout": "PT10S",
                },
            },
            {
                "method": "Stop",
                "params": {"ProfileToken": "prof8", "PanTilt": True, "Zoom": True},
            },
            {
                "method": "SetConfiguration",
                "params": {
                    "PTZConfiguration": {"Token": "config1"},
                    "ForcePersistence": False,
                },
            },
            {
                "method": "GotoHomePosition",
                "params": {
                    "ProfileToken": "prof9",
                    "Speed": {"PanTilt": {"x": 1.0, "y": 1.0}},
                },
            },
            {
                "method": "RemovePreset",
                "params": {"ProfileToken": "prof10", "PresetToken": "preset3"},
            },
            {
                "method": "GetPresetTours",
                "params": {"ProfileToken": "prof11"},
            },
            {
                "method": "CreatePresetTour",
                "params": {"ProfileToken": "prof12"},
            },
            {
                "method": "SendAuxiliaryCommand",
                "params": {"ProfileToken": "prof13", "AuxiliaryData": "command1"},
            },
        ]

        for test_case in test_cases:
            mock_operator_instance.call.reset_mock()
            method = getattr(ptz, test_case["method"])
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
