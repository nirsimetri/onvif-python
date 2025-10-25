"""
Test WSDL compliance for Search service
"""

import os
import inspect
from unittest.mock import Mock, patch
from lxml import etree
from onvif.services.search import Search


def test_search_import():
    assert Search is not None


class TestSearchWSDLCompliance:
    """Test that Search service implementation matches WSDL specification"""

    @staticmethod
    def get_wsdl_operations():
        """Parse WSDL to get all defined operations with their parameters."""
        wsdl_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "onvif",
            "wsdl",
            "ver10",
            "search.wsdl",
        )

        # Parse WSDL
        tree = etree.parse(wsdl_path)
        root = tree.getroot()

        # Namespaces
        ns = {
            "wsdl": "http://schemas.xmlsoap.org/wsdl/",
            "xs": "http://www.w3.org/2001/XMLSchema",
            "tsc": "http://www.onvif.org/ver10/search/wsdl",
        }

        operations = {}

        # Find all operations in portType
        port_type = root.find('.//wsdl:portType[@name="SearchPort"]', ns)
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
        """Get all implemented methods in Search class."""
        methods = {}
        for name, method in inspect.getmembers(Search, predicate=inspect.isfunction):
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
        """Verify all WSDL operations are implemented as methods"""
        wsdl_operations = self.get_wsdl_operations()
        implemented_methods = self.get_implemented_methods()

        missing_operations = set(wsdl_operations) - set(implemented_methods)

        assert not missing_operations, (
            f"Missing implementations for WSDL operations: {missing_operations}. "
            f"WSDL defines: {sorted(wsdl_operations)}, "
            f"Implemented: {sorted(implemented_methods)}"
        )

    def test_method_parameters_match_wsdl(self):
        """Verify method signatures match WSDL message definitions"""
        wsdl_path = os.path.join(
            os.path.dirname(__file__),
            "../../onvif/wsdl/ver10/search.wsdl",
        )
        tree = etree.parse(wsdl_path)

        namespaces = {
            "wsdl": "http://schemas.xmlsoap.org/wsdl/",
            "xs": "http://www.w3.org/2001/XMLSchema",
            "tse": "http://www.onvif.org/ver10/search/wsdl",
        }

        messages = {}
        for message in tree.xpath("//wsdl:message", namespaces=namespaces):
            message_name = message.get("name")
            parts = {}
            for part in message.findall("wsdl:part", namespaces):
                part_name = part.get("name")
                element = part.get("element")
                if element:
                    element = element.split(":")[-1]
                parts[part_name] = element
            messages[message_name] = parts

        port_type = tree.xpath(
            '//wsdl:portType[@name="SearchPort"]', namespaces=namespaces
        )[0]

        schema_elements = {}
        for element in tree.xpath("//xs:element[@name]", namespaces=namespaces):
            element_name = element.get("name")
            complex_type = element.find("xs:complexType", namespaces)
            if complex_type is not None:
                sequence = complex_type.find("xs:sequence", namespaces)
                if sequence is not None:
                    params = []
                    for elem in sequence.findall("xs:element", namespaces):
                        params.append(elem.get("name"))
                    schema_elements[element_name] = params

        mismatches = []
        for operation in port_type.findall("wsdl:operation", namespaces):
            operation_name = operation.get("name")

            input_elem = operation.find("wsdl:input", namespaces)
            if input_elem is None:
                continue

            message_name = input_elem.get("message")
            if message_name:
                message_name = message_name.split(":")[-1]

            if message_name not in messages:
                continue

            message_parts = messages[message_name]
            if "parameters" not in message_parts:
                continue

            element_name = message_parts["parameters"]
            if element_name not in schema_elements:
                continue

            expected_params = schema_elements[element_name]

            method = getattr(Search, operation_name, None)
            if method is None:
                continue

            sig = inspect.signature(method)
            actual_params = [
                p for p in sig.parameters.keys() if p not in ["self", "kwargs"]
            ]

            if set(expected_params) != set(actual_params):
                mismatches.append(
                    f"{operation_name}: expected {expected_params}, got {actual_params}"
                )

        assert not mismatches, "Parameter mismatches found:\n" + "\n".join(mismatches)

    @patch("onvif.services.search.ONVIFOperator")
    def test_operator_call_usage(self, mock_operator_class):
        """Verify all methods use operator.call for SOAP requests"""
        mock_operator = Mock()
        mock_operator_class.return_value = mock_operator

        service = Search(xaddr="http://test:80/onvif/Search")

        operations = self.get_wsdl_operations()

        for operation in operations:
            mock_operator.call.reset_mock()

            method = getattr(service, operation)
            sig = inspect.signature(method)
            params = {
                p: None for p in sig.parameters.keys() if p not in ["self", "kwargs"]
            }

            try:
                method(**params)
            except Exception:
                pass

            assert (
                mock_operator.call.called
            ), f"{operation} should use operator.call for SOAP requests"

    @patch("onvif.services.search.ONVIFOperator")
    def test_specific_methods_implementation(self, mock_operator_class):
        """Test specific Search methods"""
        mock_operator = Mock()
        mock_operator.call.return_value = {"Result": "success"}
        mock_operator_class.return_value = mock_operator

        service = Search(xaddr="http://test:80/onvif/Search")

        # Test GetServiceCapabilities (no parameters)
        service.GetServiceCapabilities()
        mock_operator.call.assert_called_with("GetServiceCapabilities")

        # Test FindRecordings
        service.FindRecordings(Scope=None, KeepAliveTime=None, MaxMatches=None)
        mock_operator.call.assert_called_with(
            "FindRecordings",
            Scope=None,
            KeepAliveTime=None,
            MaxMatches=None,
        )

        # Test GetRecordingSearchResults
        service.GetRecordingSearchResults(
            SearchToken=None, MinResults=None, MaxResults=None, WaitTime=None
        )
        mock_operator.call.assert_called_with(
            "GetRecordingSearchResults",
            SearchToken=None,
            MinResults=None,
            MaxResults=None,
            WaitTime=None,
        )

        # Test FindEvents
        service.FindEvents(
            StartPoint=None,
            Scope=None,
            SearchFilter=None,
            IncludeStartState=None,
            KeepAliveTime=None,
            EndPoint=None,
            MaxMatches=None,
        )
        mock_operator.call.assert_called_with(
            "FindEvents",
            StartPoint=None,
            Scope=None,
            SearchFilter=None,
            IncludeStartState=None,
            KeepAliveTime=None,
            EndPoint=None,
            MaxMatches=None,
        )

        # Test GetEventSearchResults
        service.GetEventSearchResults(
            SearchToken=None, MinResults=None, MaxResults=None, WaitTime=None
        )
        mock_operator.call.assert_called_with(
            "GetEventSearchResults",
            SearchToken=None,
            MinResults=None,
            MaxResults=None,
            WaitTime=None,
        )

        # Test EndSearch
        service.EndSearch(SearchToken=None)
        mock_operator.call.assert_called_with("EndSearch", SearchToken=None)

    def test_no_extra_methods(self):
        """Verify no extra public methods beyond WSDL operations"""
        wsdl_operations = set(self.get_wsdl_operations())
        implemented_methods = set(self.get_implemented_methods())

        extra_methods = implemented_methods - wsdl_operations

        assert not extra_methods, (
            f"Found public methods not defined in WSDL: {extra_methods}. "
            f"These should either be removed or made private (prefix with _)"
        )

    @patch("onvif.services.search.ONVIFOperator")
    def test_parameter_forwarding(self, mock_operator_class):
        """Verify all method parameters are properly forwarded to operator.call"""
        mock_operator = Mock()
        mock_operator_class.return_value = mock_operator

        service = Search(xaddr="http://test:80/onvif/search")

        test_cases = [
            ("GetRecordingInformation", {"RecordingToken": "token123"}),
            (
                "GetMediaAttributes",
                {"Time": "2024-01-01T00:00:00Z", "RecordingTokens": ["token1"]},
            ),
            (
                "FindRecordings",
                {
                    "Scope": {"IncludedSources": []},
                    "KeepAliveTime": "PT60S",
                    "MaxMatches": 100,
                },
            ),
            (
                "FindPTZPosition",
                {
                    "StartPoint": "2024-01-01T00:00:00Z",
                    "Scope": {"IncludedSources": []},
                    "SearchFilter": {"MinPosition": {}},
                    "KeepAliveTime": "PT60S",
                    "EndPoint": "2024-01-01T12:00:00Z",
                    "MaxMatches": 50,
                },
            ),
            ("GetSearchState", {"SearchToken": "search123"}),
        ]

        for operation, params in test_cases:
            mock_operator.call.reset_mock()
            method = getattr(service, operation)
            method(**params)
            mock_operator.call.assert_called_once_with(operation, **params)
