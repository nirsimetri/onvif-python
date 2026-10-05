# pylint: disable=protected-access
"""Tests for ONVIF interactive service commands."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import RequestException
from zeep.exceptions import Fault, TransportError

from onvif.cli.interactive.service import ServiceCommands
from onvif.utils.exceptions import ONVIFOperationException

from .conftest import strip_ansi


def create_args(**overrides):
    """Create mocked CLI arguments."""
    args = MagicMock()

    args.host = overrides.get("host", "192.168.1.100")
    args.port = overrides.get("port", 80)
    args.username = overrides.get("username", "admin")
    args.digest = overrides.get("digest", False)
    args.https = overrides.get("https", False)
    args.no_verify_ssl = overrides.get("no_verify_ssl", False)
    args.timeout = overrides.get("timeout", 10)
    args.debug = overrides.get("debug", False)
    args.no_patch = overrides.get("no_patch", False)
    args.wsdl = overrides.get("wsdl", None)
    args.health_check_interval = overrides.get("health_check_interval", 10)

    return args


def create_context(**overrides):
    """Create a mock shell context for service command tests."""
    context = MagicMock()
    context.args = create_args(**overrides)
    context.current_service = MagicMock()
    context.current_service_name = "devicemgmt"
    context.last_result = None
    context.last_method = None
    context.last_service_name = None
    context.last_operation_timestamp = None

    for key, value in overrides.items():
        setattr(context, key, value)

    return context


def create_commands(**overrides):
    """Create ServiceCommands with a mocked shell context."""
    commands = ServiceCommands()
    commands.context = create_context(**overrides)
    commands._substitute_stored_references = MagicMock()
    commands._handle_connection_error = MagicMock()
    return commands


class TestServiceCommandsExecution:
    """Test service method execution."""

    def test_execute_method_without_service(self, capsys):
        """Verify execution fails when not in service mode."""
        commands = create_commands(current_service=None)

        commands.execute_service_method("GetDeviceInformation", "")

        captured = capsys.readouterr()

        assert "Error:" in captured.out
        assert "Not in service mode" in captured.out

    def test_execute_unknown_method(self, capsys):
        """Verify unknown methods display available methods."""
        commands = create_commands()

        commands.context.current_service = MagicMock(spec=["GetDeviceInformation"])
        commands.context.current_service.GetDeviceInformation = MagicMock()

        with patch(
            "onvif.cli.interactive.service.get_service_methods",
            return_value=["GetDeviceInformation", "GetCapabilities"],
        ):
            commands.execute_service_method("UnknownMethod", "")

        captured = capsys.readouterr()

        assert "Unknown method 'UnknownMethod'" in captured.out
        assert "devicemgmt" in captured.out
        assert "Available methods:" in captured.out
        assert "GetDeviceInformation, GetCapabilities" in captured.out

    def test_execute_unknown_method_with_more_than_five_methods(self, capsys):
        """Verify long method lists suggest using ls or TAB."""
        commands = create_commands()

        commands.context.current_service = MagicMock(spec=["GetDeviceInformation"])

        methods = [
            "Method1",
            "Method2",
            "Method3",
            "Method4",
            "Method5",
            "Method6",
        ]

        with patch(
            "onvif.cli.interactive.service.get_service_methods",
            return_value=methods,
        ):
            commands.execute_service_method("UnknownMethod", "")

        captured = capsys.readouterr()

        assert "Available methods:" in captured.out
        assert "Method1, Method2, Method3, Method4, Method5" in captured.out
        assert "Type" in captured.out
        assert "ls" in captured.out

    def test_execute_method_without_parameters(self, capsys):
        """Verify a service method is called without parameters."""
        method = MagicMock(return_value={"Manufacturer": "Test"})
        commands = create_commands()
        commands.context.current_service.GetDeviceInformation = method

        commands.execute_service_method("GetDeviceInformation", "")

        method.assert_called_once_with()
        captured = capsys.readouterr()

        assert "{'Manufacturer': 'Test'}" in captured.out
        assert commands.context.last_result == {"Manufacturer": "Test"}
        assert commands.context.last_method == "GetDeviceInformation"
        assert commands.context.last_service_name == "devicemgmt"
        assert isinstance(commands.context.last_operation_timestamp, datetime)

    def test_execute_method_with_json_parameters(self, capsys):
        """Verify JSON parameters are parsed and passed to the service method."""
        method = MagicMock(return_value="result")
        commands = create_commands()
        commands.context.current_service.GetCapabilities = method

        with patch(
            "onvif.cli.interactive.service.parse_json_params",
            return_value={"Category": "All"},
        ) as parse_mock:
            commands.execute_service_method(
                "GetCapabilities",
                '{"Category": "All"}',
            )

        parse_mock.assert_called_once_with('{"Category": "All"}')
        method.assert_called_once_with(Category="All")

        captured = capsys.readouterr()
        assert "result" in captured.out

    def test_execute_method_substitutes_stored_references(self):
        """Verify stored references are substituted before JSON parsing."""
        method = MagicMock(return_value="result")
        commands = create_commands()
        commands.context.current_service.GetCapabilities = method
        commands._substitute_stored_references.return_value = '{"Category": "All"}'

        commands.execute_service_method(
            "GetCapabilities",
            '{"Category": "$stored"}',
        )

        commands._substitute_stored_references.assert_called_once_with(
            '{"Category": "$stored"}'
        )
        method.assert_called_once_with(Category="All")

    def test_execute_method_without_dollar_does_not_substitute(self):
        """Verify reference substitution is skipped when no dollar sign exists."""
        method = MagicMock(return_value="result")
        commands = create_commands()
        commands.context.current_service.TestMethod = method

        with patch(
            "onvif.cli.interactive.service.parse_json_params",
            return_value={"value": "test"},
        ):
            commands.execute_service_method(
                "TestMethod",
                '{"value": "test"}',
            )

        commands._substitute_stored_references.assert_not_called()

    def test_execute_method_updates_last_operation_state(self):
        """Verify successful execution stores result metadata."""
        result = {"value": 123}
        method = MagicMock(return_value=result)
        commands = create_commands()
        commands.context.current_service.TestMethod = method

        before = datetime.now()
        commands.execute_service_method("TestMethod", "")
        after = datetime.now()

        assert commands.context.last_result == result
        assert commands.context.last_method == "TestMethod"
        assert commands.context.last_service_name == "devicemgmt"
        assert before <= commands.context.last_operation_timestamp <= after

    @pytest.mark.parametrize(
        "exception",
        [
            ValueError("invalid value"),
            TypeError("invalid argument"),
            ONVIFOperationException("FailedOperation", RuntimeError("Error")),
        ],
    )
    def test_execute_method_handles_regular_errors(self, exception, capsys):
        """Verify regular operation errors are displayed without exiting."""
        method = MagicMock(side_effect=exception)
        commands = create_commands()
        commands.context.current_service.TestMethod = method

        commands.execute_service_method("TestMethod", "")

        captured = capsys.readouterr()

        assert "Error:" in captured.out
        assert str(exception) in captured.out
        commands._handle_connection_error.assert_not_called()

    @pytest.mark.parametrize(
        "original_exception",
        [
            RequestException("request failed"),
            TransportError("transport failed"),
        ],
    )
    def test_execute_method_handles_connection_errors(self, original_exception):
        """Verify wrapped connection errors invoke the connection handler."""
        exception = ONVIFOperationException(
            "operation failed",
            original_exception=original_exception,
        )
        method = MagicMock(side_effect=exception)
        commands = create_commands()
        commands.context.current_service.TestMethod = method

        commands.execute_service_method("TestMethod", "")

        commands._handle_connection_error.assert_called_once_with()

    def test_execute_method_handles_soap_fault_without_traceback(self, capsys):
        """Verify SOAP faults are printed without a debug traceback."""
        original_exception = Fault("SOAP operation failed")
        exception = ONVIFOperationException(
            "operation failed",
            original_exception=original_exception,
        )

        method = MagicMock(side_effect=exception)
        commands = create_commands(debug=True)
        commands.context.current_service.TestMethod = method

        with patch("onvif.cli.interactive.service.traceback.print_exc") as print_exc:
            commands.execute_service_method("TestMethod", "")

        print_exc.assert_not_called()

        captured = capsys.readouterr()
        assert "Error:" in captured.out

    def test_execute_method_does_not_print_traceback_without_debug(
        self,
    ):
        """Verify regular errors do not print tracebacks when debug is disabled."""
        exception = ONVIFOperationException("unexpected failure", TypeError)
        method = MagicMock(side_effect=exception)
        commands = create_commands(debug=False)
        commands.context.current_service.TestMethod = method

        with patch("onvif.cli.interactive.service.traceback.print_exc") as print_exc:
            commands.execute_service_method("TestMethod", "")

        print_exc.assert_not_called()

    def test_type_error_does_not_print_debug_traceback(self):
        """Verify TypeError is treated as a common user error."""
        exception = TypeError("missing argument")
        method = MagicMock(side_effect=exception)
        commands = create_commands(debug=True)
        commands.context.current_service.TestMethod = method

        with patch("onvif.cli.interactive.service.traceback.print_exc") as print_exc:
            commands.execute_service_method("TestMethod", "")

        print_exc.assert_not_called()


class TestServiceCommandsDescription:
    """Test the desc command."""

    def test_desc_without_service(self, capsys):
        """Verify desc requires service mode."""
        commands = create_commands(current_service=None)

        commands.do_desc("GetDeviceInformation")

        captured = capsys.readouterr()

        assert "must be in a service mode" in captured.out
        assert "Enter a service first" in captured.out

    def test_desc_without_method_name(self, capsys):
        """Verify desc displays usage without a method name."""
        commands = create_commands()

        commands.do_desc("")

        captured = capsys.readouterr()

        assert "Usage: desc <method_name>" in captured.out

    def test_desc_unknown_method(self, capsys):
        """Verify desc handles an unknown method."""
        commands = create_commands()
        commands.context.current_service = MagicMock(spec=["KnownMethod"])

        commands.do_desc("UnknownMethod")

        captured = capsys.readouterr()

        assert "Method 'UnknownMethod' not found" in captured.out
        assert "Use" in captured.out
        assert "ls" in captured.out

    def test_desc_without_documentation(self, capsys):
        """Verify desc handles missing documentation."""
        commands = create_commands()
        commands.context.current_service = MagicMock(spec=["KnownMethod"])

        with patch(
            "onvif.cli.interactive.service.get_method_documentation",
            return_value=None,
        ):
            commands.do_desc("KnownMethod")

        captured = capsys.readouterr()

        assert (
            "No documentation or parameter info found for method 'KnownMethod'."
            in captured.out
        )

    def test_desc_displays_documentation(self, capsys):
        """Verify desc displays method documentation."""
        commands = create_commands()
        commands.context.current_service = MagicMock(spec=["KnownMethod"])

        doc_info = {
            "doc": "Retrieve device information.\nReturns manufacturer details.",
            "required": [],
            "optional": [],
        }

        with patch(
            "onvif.cli.interactive.service.get_method_documentation",
            return_value=doc_info,
        ):
            commands.do_desc("KnownMethod")

        captured = strip_ansi(capsys.readouterr().out)

        assert "Description for devicemgmt.KnownMethod():" in captured
        assert "Retrieve device information." in captured
        assert "Returns manufacturer details." in captured

    def test_desc_displays_required_and_optional_arguments(self, capsys):
        """Verify desc displays required and optional arguments."""
        commands = create_commands()
        commands.context.current_service = MagicMock(spec=["KnownMethod"])

        doc_info = {
            "doc": "Test method.",
            "required": ["Device", "Token"],
            "optional": ["Timeout", "Profile"],
        }

        with patch(
            "onvif.cli.interactive.service.get_method_documentation",
            return_value=doc_info,
        ):
            commands.do_desc("KnownMethod")

        captured = capsys.readouterr()

        assert "Required Arguments:" in captured.out
        assert "  - Device" in captured.out
        assert "  - Token" in captured.out
        assert "Optional Arguments:" in captured.out
        assert "  - Timeout" in captured.out
        assert "  - Profile" in captured.out

    def test_desc_wraps_long_documentation(self, capsys):
        """Verify long documentation is wrapped to the configured width."""
        commands = create_commands()
        commands.context.current_service = MagicMock(spec=["KnownMethod"])

        long_text = "A " * 100
        doc_info = {
            "doc": long_text,
            "required": [],
            "optional": [],
        }

        with patch(
            "onvif.cli.interactive.service.get_method_documentation",
            return_value=doc_info,
        ):
            commands.do_desc("KnownMethod")

        captured = strip_ansi(capsys.readouterr().out)

        assert "Description for devicemgmt.KnownMethod():" in captured
        assert len(captured.splitlines()) > 2

    def test_complete_desc_without_service(self):
        """Verify desc completion returns nothing outside service mode."""
        commands = create_commands(current_service=None)

        assert commands.complete_desc("Get", "", 0, 3) == []

    def test_complete_desc_matches_methods_case_insensitively(self):
        """Verify desc completion matches method names case-insensitively."""
        commands = create_commands()

        with patch(
            "onvif.cli.interactive.service.get_service_methods",
            return_value=[
                "GetDeviceInformation",
                "GetCapabilities",
                "SetSystemDateAndTime",
            ],
        ):
            result = commands.complete_desc("get", "", 0, 3)

        assert result == ["GetDeviceInformation", "GetCapabilities"]


class TestServiceCommandsType:
    """Test the type command."""

    def test_type_without_service(self, capsys):
        """Verify type requires service mode."""
        commands = create_commands(current_service=None)

        commands.do_type("GetDeviceInformation")

        captured = capsys.readouterr()

        assert "must be in a service mode" in captured.out
        assert "Enter a service first" in captured.out

    def test_type_without_method_name(self, capsys):
        """Verify type displays usage without a method name."""
        commands = create_commands()

        commands.do_type("")

        captured = capsys.readouterr()

        assert "Usage: type <method_name>" in captured.out

    def test_type_unknown_method(self, capsys):
        """Verify type handles an unknown method."""
        commands = create_commands()
        commands.context.current_service = MagicMock(spec=["KnownMethod"])

        commands.do_type("UnknownMethod")

        captured = capsys.readouterr()

        assert "Method 'UnknownMethod' not found" in captured.out
        assert "Use" in captured.out
        assert "ls" in captured.out

    def test_type_without_type_information(self, capsys):
        """Verify type handles unavailable type information."""
        commands = create_commands()
        commands.context.current_service = MagicMock(spec=["KnownMethod"])

        with patch(
            "onvif.cli.interactive.service.get_operation_type_info",
            return_value=None,
        ):
            commands.do_type("KnownMethod")

        captured = capsys.readouterr()

        assert "Could not retrieve type information" in captured.out

    def test_type_displays_input_and_output(self, capsys):
        """Verify type displays basic input and output information."""
        commands = create_commands()
        commands.context.current_service = MagicMock(spec=["TestMethod"])

        type_info = {
            "input": {
                "name": "TestMethodRequest",
                "parameters": [],
            },
            "output": {
                "name": "TestMethodResponse",
                "parameters": [],
            },
        }

        with patch(
            "onvif.cli.interactive.service.get_operation_type_info",
            return_value=type_info,
        ):
            commands.do_type("TestMethod")

        captured = capsys.readouterr()

        assert "Input:" in captured.out
        assert "[TestMethodRequest]" in captured.out
        assert "(no parameters)" in captured.out
        assert "Output:" in captured.out
        assert "[TestMethodResponse]" in captured.out

    def test_type_displays_missing_input_and_output(self, capsys):
        """Verify type displays undefined input and output messages."""
        commands = create_commands()
        commands.context.current_service = MagicMock(spec=["TestMethod"])

        type_info = {
            "input": None,
            "output": None,
        }

        with patch(
            "onvif.cli.interactive.service.get_operation_type_info",
            return_value=type_info,
        ):
            commands.do_type("TestMethod")

        captured = capsys.readouterr()

        assert "Input:" in captured.out
        assert "(not defined)" in captured.out
        assert "Output:" in captured.out

    def test_type_displays_required_optional_and_unbounded_parameters(self, capsys):
        """Verify type displays parameter occurrence information."""
        commands = create_commands()
        commands.context.current_service = MagicMock(spec=["TestMethod"])

        type_info = {
            "input": {
                "name": "TestMethodRequest",
                "parameters": [
                    {
                        "name": "RequiredParam",
                        "type": "string",
                        "minOccurs": "1",
                        "maxOccurs": "1",
                    },
                    {
                        "name": "OptionalParam",
                        "type": "int",
                        "minOccurs": "0",
                        "maxOccurs": "1",
                    },
                    {
                        "name": "ListParam",
                        "type": "string",
                        "minOccurs": "0",
                        "maxOccurs": "unbounded",
                    },
                ],
            },
            "output": None,
        }

        with patch(
            "onvif.cli.interactive.service.get_operation_type_info",
            return_value=type_info,
        ):
            commands.do_type("TestMethod")

        captured = strip_ansi(capsys.readouterr().out)

        assert "+RequiredParam" not in captured
        assert "-RequiredParam" in captured
        assert "[string]" in captured
        assert "required" in captured
        assert "OptionalParam" in captured
        assert "optional" in captured
        assert "ListParam" in captured
        assert "unbounded" in captured

    def test_type_displays_attributes(self, capsys):
        """Verify attributes use the plus prefix and required occurrence."""
        commands = create_commands()
        commands.context.current_service = MagicMock(spec=["TestMethod"])

        type_info = {
            "input": {
                "name": "TestRequest",
                "parameters": [
                    {
                        "name": "OptionalAttribute",
                        "type": "string",
                        "minOccurs": "0",
                        "maxOccurs": "1",
                        "is_attribute": True,
                    },
                    {
                        "name": "RequiredAttribute",
                        "type": "string",
                        "minOccurs": "1",
                        "maxOccurs": "1",
                        "is_attribute": True,
                    },
                ],
            },
            "output": None,
        }

        with patch(
            "onvif.cli.interactive.service.get_operation_type_info",
            return_value=type_info,
        ):
            commands.do_type("TestMethod")

        captured = strip_ansi(capsys.readouterr().out)

        assert "+OptionalAttribute" in captured
        assert "+RequiredAttribute" in captured
        assert "required" in captured

    def test_type_displays_nested_parameters(self, capsys):
        """Verify nested parameters use tree-style formatting."""
        commands = create_commands()
        commands.context.current_service = MagicMock(spec=["TestMethod"])

        type_info = {
            "input": {
                "name": "TestRequest",
                "parameters": [
                    {
                        "name": "Parent",
                        "type": "ParentType",
                        "minOccurs": "1",
                        "maxOccurs": "1",
                        "children": [
                            {
                                "name": "ChildOne",
                                "type": "string",
                                "minOccurs": "1",
                                "maxOccurs": "1",
                            },
                            {
                                "name": "ChildTwo",
                                "type": "int",
                                "minOccurs": "0",
                                "maxOccurs": "1",
                            },
                        ],
                    }
                ],
            },
            "output": None,
        }

        with patch(
            "onvif.cli.interactive.service.get_operation_type_info",
            return_value=type_info,
        ):
            commands.do_type("TestMethod")

        captured = capsys.readouterr()

        assert "Parent" in captured.out
        assert "ChildOne" in captured.out
        assert "ChildTwo" in captured.out
        assert "├──" in captured.out
        assert "└──" in captured.out

    def test_type_displays_parameter_documentation(self, capsys):
        """Verify parameter documentation is displayed."""
        commands = create_commands()
        commands.context.current_service = MagicMock(spec=["TestMethod"])

        type_info = {
            "input": {
                "name": "TestRequest",
                "parameters": [
                    {
                        "name": "Token",
                        "type": "string",
                        "minOccurs": "1",
                        "maxOccurs": "1",
                        "documentation": "Identifier used to select the profile.",
                    }
                ],
            },
            "output": None,
        }

        with patch(
            "onvif.cli.interactive.service.get_operation_type_info",
            return_value=type_info,
        ):
            commands.do_type("TestMethod")

        captured = capsys.readouterr()

        assert "Token" in captured.out
        assert "Identifier used to select the profile." in captured.out

    def test_type_displays_multiline_documentation(self, capsys):
        """Verify multiline parameter documentation is displayed."""
        commands = create_commands()
        commands.context.current_service = MagicMock(spec=["TestMethod"])

        type_info = {
            "input": {
                "name": "TestRequest",
                "parameters": [
                    {
                        "name": "Token",
                        "type": "string",
                        "minOccurs": "1",
                        "maxOccurs": "1",
                        "documentation": ("First line.\n" "\n" "Second line."),
                    }
                ],
            },
            "output": None,
        }

        with patch(
            "onvif.cli.interactive.service.get_operation_type_info",
            return_value=type_info,
        ):
            commands.do_type("TestMethod")

        captured = capsys.readouterr()

        assert "First line." in captured.out
        assert "Second line." in captured.out

    def test_type_handles_empty_output_parameters(self, capsys):
        """Verify empty output parameters are displayed correctly."""
        commands = create_commands()
        commands.context.current_service = MagicMock(spec=["TestMethod"])

        type_info = {
            "input": None,
            "output": {
                "name": "TestResponse",
                "parameters": [],
            },
        }

        with patch(
            "onvif.cli.interactive.service.get_operation_type_info",
            return_value=type_info,
        ):
            commands.do_type("TestMethod")

        captured = capsys.readouterr()

        assert "[TestResponse]" in captured.out
        assert "(no parameters)" in captured.out

    def test_complete_type_without_service(self):
        """Verify type completion returns nothing outside service mode."""
        commands = create_commands(current_service=None)

        assert commands.complete_type("Get", "", 0, 3) == []

    def test_complete_type_matches_methods_case_insensitively(self):
        """Verify type completion matches method names case-insensitively."""
        commands = create_commands()

        with patch(
            "onvif.cli.interactive.service.get_service_methods",
            return_value=[
                "GetDeviceInformation",
                "GetCapabilities",
                "SetSystemDateAndTime",
            ],
        ):
            result = commands.complete_type("get", "", 0, 3)

        assert result == ["GetDeviceInformation", "GetCapabilities"]
