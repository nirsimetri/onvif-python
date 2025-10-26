from onvif.services import Search
from base_service_test import ONVIFServiceTestBase


class TestSearchWSDLCompliance(ONVIFServiceTestBase):
    """Test that Search service implementation matches WSDL specification"""

    # Service configuration
    SERVICE_CLASS = Search
    SERVICE_NAME = "search"
    WSDL_PATH_COMPONENTS = ["ver10", "search.wsdl"]
    BINDING_NAME = "SearchBinding"
    NAMESPACE_PREFIX = "tsc"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/search/wsdl"
    XADDR_PATH = "/onvif/SearchRecording"

    def test_specific_methods_implementation(self):
        """Test specific Search methods"""
        test_cases = [
            {"method": "GetServiceCapabilities", "params": {}},
            {
                "method": "FindRecordings",
                "params": {"Scope": None, "KeepAliveTime": None, "MaxMatches": None},
            },
            {
                "method": "GetRecordingSearchResults",
                "params": {
                    "SearchToken": None,
                    "MinResults": None,
                    "MaxResults": None,
                    "WaitTime": None,
                },
            },
            {
                "method": "FindEvents",
                "params": {
                    "StartPoint": None,
                    "Scope": None,
                    "SearchFilter": None,
                    "IncludeStartState": None,
                    "KeepAliveTime": None,
                    "EndPoint": None,
                    "MaxMatches": None,
                },
            },
            {
                "method": "GetEventSearchResults",
                "params": {
                    "SearchToken": None,
                    "MinResults": None,
                    "MaxResults": None,
                    "WaitTime": None,
                },
            },
            {"method": "EndSearch", "params": {"SearchToken": None}},
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Verify all method parameters are properly forwarded to operator.call"""
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

        formatted_test_cases = [
            {"method": operation, "params": params} for operation, params in test_cases
        ]
        self.run_parameter_forwarding_tests(formatted_test_cases)
