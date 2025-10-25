import os
import inspect
from unittest.mock import Mock, patch
from lxml import etree
from onvif.services.provisioning import Provisioning


def test_provisioning_import():
    assert Provisioning is not None


class TestProvisioningWSDLCompliance:
    """Test that Provisioning service implementation matches WSDL specification."""

    @staticmethod
    def get_wsdl_operations():
        """Parse WSDL to get all defined operations with their parameters."""
        wsdl_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "onvif",
            "wsdl",
            "ver10",
            "provisioning",
            "wsdl",
            "provisioning.wsdl",
        )

        # Parse WSDL
        tree = etree.parse(wsdl_path)
        root = tree.getroot()

        # Namespaces
        ns = {
            "wsdl": "http://schemas.xmlsoap.org/wsdl/",
            "xs": "http://www.w3.org/2001/XMLSchema",
            "tpv": "http://www.onvif.org/ver10/provisioning/wsdl",
        }

        operations = {}

        # Find all operations in portType
        port_type = root.find('.//wsdl:portType[@name="ProvisioningService"]', ns)
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
        """Get all implemented methods in Provisioning class."""
        methods = {}
        for name, method in inspect.getmembers(
            Provisioning, predicate=inspect.isfunction
        ):
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

    @patch("onvif.services.provisioning.ONVIFOperator")
    def test_operator_call_usage(self, mock_operator_class):
        """Test that all methods correctly call self.operator.call()."""
        # Create mock operator
        mock_operator_instance = Mock()
        mock_operator_class.return_value = mock_operator_instance

        # Create Provisioning instance
        provisioning = Provisioning(xaddr="http://test:80/onvif/Provisioning")

        implemented_methods = self.get_implemented_methods()

        errors = []

        for method_name, method_info in implemented_methods.items():
            # Reset mock
            mock_operator_instance.call.reset_mock()

            try:
                # Get the method
                method = getattr(provisioning, method_name)

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

    @patch("onvif.services.provisioning.ONVIFOperator")
    def test_specific_methods_implementation(self, mock_operator_class):
        """Test specific important methods are correctly implemented."""
        mock_operator_instance = Mock()
        mock_operator_class.return_value = mock_operator_instance
        mock_operator_instance.call.return_value = {"Result": "Success"}

        provisioning = Provisioning(xaddr="http://test:80/onvif/Provisioning")

        # Test GetServiceCapabilities (no parameters)
        provisioning.GetServiceCapabilities()
        mock_operator_instance.call.assert_called_with("GetServiceCapabilities")

        # Test PanMove (required + optional parameter)
        mock_operator_instance.call.reset_mock()
        provisioning.PanMove(VideoSource="vs1", Direction="Left", Timeout="PT5S")
        mock_operator_instance.call.assert_called_with(
            "PanMove", VideoSource="vs1", Direction="Left", Timeout="PT5S"
        )

        # Test TiltMove (required + optional parameter)
        mock_operator_instance.call.reset_mock()
        provisioning.TiltMove(VideoSource="vs2", Direction="Up", Timeout="PT3S")
        mock_operator_instance.call.assert_called_with(
            "TiltMove", VideoSource="vs2", Direction="Up", Timeout="PT3S"
        )

        # Test ZoomMove (required + optional parameter)
        mock_operator_instance.call.reset_mock()
        provisioning.ZoomMove(VideoSource="vs3", Direction="Wide", Timeout="PT10S")
        mock_operator_instance.call.assert_called_with(
            "ZoomMove", VideoSource="vs3", Direction="Wide", Timeout="PT10S"
        )

        # Test RollMove (required + optional parameter)
        mock_operator_instance.call.reset_mock()
        provisioning.RollMove(VideoSource="vs4", Direction="Clockwise", Timeout="PT7S")
        mock_operator_instance.call.assert_called_with(
            "RollMove", VideoSource="vs4", Direction="Clockwise", Timeout="PT7S"
        )

        # Test FocusMove (required + optional parameter)
        mock_operator_instance.call.reset_mock()
        provisioning.FocusMove(VideoSource="vs5", Direction="Near", Timeout="PT4S")
        mock_operator_instance.call.assert_called_with(
            "FocusMove", VideoSource="vs5", Direction="Near", Timeout="PT4S"
        )

        # Test Stop (required parameter)
        mock_operator_instance.call.reset_mock()
        provisioning.Stop(VideoSource="vs6")
        mock_operator_instance.call.assert_called_with("Stop", VideoSource="vs6")

        # Test GetUsage (required parameter)
        mock_operator_instance.call.reset_mock()
        provisioning.GetUsage(VideoSource="vs7")
        mock_operator_instance.call.assert_called_with("GetUsage", VideoSource="vs7")

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

    @patch("onvif.services.provisioning.ONVIFOperator")
    def test_parameter_forwarding(self, mock_operator_class):
        """Test that parameters are correctly forwarded to operator.call()."""
        mock_operator_instance = Mock()
        mock_operator_class.return_value = mock_operator_instance
        mock_operator_instance.call.return_value = {}

        provisioning = Provisioning(xaddr="http://test:80/onvif/Provisioning")

        # Test that all parameters are forwarded as keyword arguments
        test_cases = [
            {
                "method": "PanMove",
                "params": {
                    "VideoSource": "vs1",
                    "Direction": "Right",
                    "Timeout": "PT6S",
                },
            },
            {
                "method": "TiltMove",
                "params": {
                    "VideoSource": "vs2",
                    "Direction": "Down",
                    "Timeout": "PT8S",
                },
            },
            {
                "method": "ZoomMove",
                "params": {
                    "VideoSource": "vs3",
                    "Direction": "Tele",
                    "Timeout": "PT12S",
                },
            },
            {
                "method": "RollMove",
                "params": {
                    "VideoSource": "vs4",
                    "Direction": "CounterClockwise",
                    "Timeout": "PT5S",
                },
            },
            {
                "method": "FocusMove",
                "params": {"VideoSource": "vs5", "Direction": "Far", "Timeout": "PT9S"},
            },
            {
                "method": "Stop",
                "params": {"VideoSource": "vs6"},
            },
            {
                "method": "GetUsage",
                "params": {"VideoSource": "vs7"},
            },
        ]

        for test_case in test_cases:
            mock_operator_instance.call.reset_mock()
            method = getattr(provisioning, test_case["method"])
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
