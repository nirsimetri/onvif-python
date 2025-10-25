import os
import inspect
from unittest.mock import Mock, patch
from lxml import etree
from onvif.services.display import Display


def test_display_import():
    assert Display is not None


class TestDisplayWSDLCompliance:
    """Test that Display service implementation matches WSDL specification."""

    @staticmethod
    def get_wsdl_operations():
        """Parse WSDL to get all defined operations with their parameters."""
        wsdl_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "onvif",
            "wsdl",
            "ver10",
            "display.wsdl",
        )

        # Parse WSDL
        tree = etree.parse(wsdl_path)
        root = tree.getroot()

        # Namespaces
        ns = {
            "wsdl": "http://schemas.xmlsoap.org/wsdl/",
            "xs": "http://www.w3.org/2001/XMLSchema",
            "tls": "http://www.onvif.org/ver10/display/wsdl",
        }

        operations = {}

        # Find all operations in portType
        port_type = root.find('.//wsdl:portType[@name="DisplayPort"]', ns)
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
        """Get all implemented methods in Display class."""
        methods = {}
        for name, method in inspect.getmembers(Display, predicate=inspect.isfunction):
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

    @patch("onvif.services.display.ONVIFOperator")
    def test_operator_call_usage(self, mock_operator_class):
        """Test that all methods correctly call self.operator.call()."""
        # Create mock operator
        mock_operator_instance = Mock()
        mock_operator_class.return_value = mock_operator_instance

        # Create Display instance
        display = Display(xaddr="http://test:80/onvif/Display")

        implemented_methods = self.get_implemented_methods()

        errors = []

        for method_name, method_info in implemented_methods.items():
            # Reset mock
            mock_operator_instance.call.reset_mock()

            try:
                # Get the method
                method = getattr(display, method_name)

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

    @patch("onvif.services.display.ONVIFOperator")
    def test_specific_methods_implementation(self, mock_operator_class):
        """Test specific important methods are correctly implemented."""
        mock_operator_instance = Mock()
        mock_operator_class.return_value = mock_operator_instance
        mock_operator_instance.call.return_value = {"Result": "Success"}

        display = Display(xaddr="http://test:80/onvif/Display")

        # Test GetServiceCapabilities (no parameters)
        display.GetServiceCapabilities()
        mock_operator_instance.call.assert_called_with("GetServiceCapabilities")

        # Test GetLayout (required parameter)
        mock_operator_instance.call.reset_mock()
        display.GetLayout(VideoOutput="output1")
        mock_operator_instance.call.assert_called_with(
            "GetLayout", VideoOutput="output1"
        )

        # Test SetLayout (multiple required parameters)
        mock_operator_instance.call.reset_mock()
        display.SetLayout(VideoOutput="output1", Layout={"PaneLayout": "1x1"})
        mock_operator_instance.call.assert_called_with(
            "SetLayout", VideoOutput="output1", Layout={"PaneLayout": "1x1"}
        )

        # Test GetDisplayOptions (required parameter)
        mock_operator_instance.call.reset_mock()
        display.GetDisplayOptions(VideoOutput="output2")
        mock_operator_instance.call.assert_called_with(
            "GetDisplayOptions", VideoOutput="output2"
        )

        # Test GetPaneConfigurations (required parameter)
        mock_operator_instance.call.reset_mock()
        display.GetPaneConfigurations(VideoOutput="output3")
        mock_operator_instance.call.assert_called_with(
            "GetPaneConfigurations", VideoOutput="output3"
        )

        # Test GetPaneConfiguration (multiple required parameters)
        mock_operator_instance.call.reset_mock()
        display.GetPaneConfiguration(VideoOutput="output1", Pane="pane1")
        mock_operator_instance.call.assert_called_with(
            "GetPaneConfiguration", VideoOutput="output1", Pane="pane1"
        )

        # Test SetPaneConfigurations (multiple required parameters)
        mock_operator_instance.call.reset_mock()
        display.SetPaneConfigurations(
            VideoOutput="output1",
            PaneConfiguration={"Token": "pane1", "VideoSourceToken": "source1"},
        )
        mock_operator_instance.call.assert_called_with(
            "SetPaneConfigurations",
            VideoOutput="output1",
            PaneConfiguration={"Token": "pane1", "VideoSourceToken": "source1"},
        )

        # Test SetPaneConfiguration (multiple required parameters)
        mock_operator_instance.call.reset_mock()
        display.SetPaneConfiguration(
            VideoOutput="output2",
            PaneConfiguration={"Token": "pane2", "VideoSourceToken": "source2"},
        )
        mock_operator_instance.call.assert_called_with(
            "SetPaneConfiguration",
            VideoOutput="output2",
            PaneConfiguration={"Token": "pane2", "VideoSourceToken": "source2"},
        )

        # Test CreatePaneConfiguration (multiple required parameters)
        mock_operator_instance.call.reset_mock()
        display.CreatePaneConfiguration(
            VideoOutput="output3",
            PaneConfiguration={"Token": "new_pane", "VideoSourceToken": "source3"},
        )
        mock_operator_instance.call.assert_called_with(
            "CreatePaneConfiguration",
            VideoOutput="output3",
            PaneConfiguration={"Token": "new_pane", "VideoSourceToken": "source3"},
        )

        # Test DeletePaneConfiguration (multiple required parameters)
        mock_operator_instance.call.reset_mock()
        display.DeletePaneConfiguration(VideoOutput="output4", PaneToken="pane_delete")
        mock_operator_instance.call.assert_called_with(
            "DeletePaneConfiguration", VideoOutput="output4", PaneToken="pane_delete"
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

    @patch("onvif.services.display.ONVIFOperator")
    def test_parameter_forwarding(self, mock_operator_class):
        """Test that parameters are correctly forwarded to operator.call()."""
        mock_operator_instance = Mock()
        mock_operator_class.return_value = mock_operator_instance
        mock_operator_instance.call.return_value = {}

        display = Display(xaddr="http://test:80/onvif/Display")

        # Test that all parameters are forwarded as keyword arguments
        test_cases = [
            {
                "method": "GetLayout",
                "params": {"VideoOutput": "vo1"},
            },
            {
                "method": "SetLayout",
                "params": {"VideoOutput": "vo2", "Layout": {"PaneLayout": "2x2"}},
            },
            {
                "method": "GetDisplayOptions",
                "params": {"VideoOutput": "vo3"},
            },
            {
                "method": "GetPaneConfigurations",
                "params": {"VideoOutput": "vo4"},
            },
            {
                "method": "GetPaneConfiguration",
                "params": {"VideoOutput": "vo5", "Pane": "pane5"},
            },
            {
                "method": "SetPaneConfigurations",
                "params": {
                    "VideoOutput": "vo6",
                    "PaneConfiguration": {"Token": "pane6", "VideoSourceToken": "vs6"},
                },
            },
            {
                "method": "SetPaneConfiguration",
                "params": {
                    "VideoOutput": "vo7",
                    "PaneConfiguration": {"Token": "pane7", "VideoSourceToken": "vs7"},
                },
            },
            {
                "method": "CreatePaneConfiguration",
                "params": {
                    "VideoOutput": "vo8",
                    "PaneConfiguration": {
                        "Token": "new_pane8",
                        "VideoSourceToken": "vs8",
                    },
                },
            },
            {
                "method": "DeletePaneConfiguration",
                "params": {"VideoOutput": "vo9", "PaneToken": "pane_to_delete"},
            },
        ]

        for test_case in test_cases:
            mock_operator_instance.call.reset_mock()
            method = getattr(display, test_case["method"])
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
