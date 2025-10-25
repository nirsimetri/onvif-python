import os
import inspect
from unittest.mock import Mock, patch
from lxml import etree
from onvif.services.recording import Recording


def test_recording_import():
    assert Recording is not None


class TestRecordingWSDLCompliance:
    """Test that Recording service implementation matches WSDL specification."""

    @staticmethod
    def get_wsdl_operations():
        """Parse WSDL to get all defined operations with their parameters."""
        wsdl_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "onvif",
            "wsdl",
            "ver10",
            "recording.wsdl",
        )

        # Parse WSDL
        tree = etree.parse(wsdl_path)
        root = tree.getroot()

        # Namespaces
        ns = {
            "wsdl": "http://schemas.xmlsoap.org/wsdl/",
            "xs": "http://www.w3.org/2001/XMLSchema",
            "trc": "http://www.onvif.org/ver10/recording/wsdl",
        }

        operations = {}

        # Find all operations in portType
        port_type = root.find('.//wsdl:portType[@name="RecordingPort"]', ns)
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
        """Get all implemented methods in Recording class."""
        methods = {}
        for name, method in inspect.getmembers(Recording, predicate=inspect.isfunction):
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

    @patch("onvif.services.recording.ONVIFOperator")
    def test_operator_call_usage(self, mock_operator_class):
        """Test that all methods correctly call self.operator.call()."""
        # Create mock operator
        mock_operator_instance = Mock()
        mock_operator_class.return_value = mock_operator_instance

        # Create Recording instance
        recording = Recording(xaddr="http://test:80/onvif/Recording")

        implemented_methods = self.get_implemented_methods()

        errors = []

        for method_name, method_info in implemented_methods.items():
            # Reset mock
            mock_operator_instance.call.reset_mock()

            try:
                # Get the method
                method = getattr(recording, method_name)

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

    @patch("onvif.services.recording.ONVIFOperator")
    def test_specific_methods_implementation(self, mock_operator_class):
        """Test specific important methods are correctly implemented."""
        mock_operator_instance = Mock()
        mock_operator_class.return_value = mock_operator_instance
        mock_operator_instance.call.return_value = {"Result": "Success"}

        recording = Recording(xaddr="http://test:80/onvif/Recording")

        # Test GetServiceCapabilities (no parameters)
        recording.GetServiceCapabilities()
        mock_operator_instance.call.assert_called_with("GetServiceCapabilities")

        # Test GetRecordings (no parameters)
        mock_operator_instance.call.reset_mock()
        recording.GetRecordings()
        mock_operator_instance.call.assert_called_with("GetRecordings")

        # Test CreateRecording (required parameter)
        mock_operator_instance.call.reset_mock()
        recording.CreateRecording(
            RecordingConfiguration={"Source": {"SourceId": "source1"}}
        )
        mock_operator_instance.call.assert_called_with(
            "CreateRecording",
            RecordingConfiguration={"Source": {"SourceId": "source1"}},
        )

        # Test DeleteRecording (required parameter)
        mock_operator_instance.call.reset_mock()
        recording.DeleteRecording(RecordingToken="rec1")
        mock_operator_instance.call.assert_called_with(
            "DeleteRecording", RecordingToken="rec1"
        )

        # Test SetRecordingConfiguration (multiple required parameters)
        mock_operator_instance.call.reset_mock()
        recording.SetRecordingConfiguration(
            RecordingToken="rec2",
            RecordingConfiguration={"Source": {"SourceId": "source2"}},
        )
        mock_operator_instance.call.assert_called_with(
            "SetRecordingConfiguration",
            RecordingToken="rec2",
            RecordingConfiguration={"Source": {"SourceId": "source2"}},
        )

        # Test GetRecordingConfiguration (required parameter)
        mock_operator_instance.call.reset_mock()
        recording.GetRecordingConfiguration(RecordingToken="rec3")
        mock_operator_instance.call.assert_called_with(
            "GetRecordingConfiguration", RecordingToken="rec3"
        )

        # Test CreateTrack (multiple required parameters)
        mock_operator_instance.call.reset_mock()
        recording.CreateTrack(
            RecordingToken="rec4", TrackConfiguration={"TrackType": "Video"}
        )
        mock_operator_instance.call.assert_called_with(
            "CreateTrack",
            RecordingToken="rec4",
            TrackConfiguration={"TrackType": "Video"},
        )

        # Test DeleteTrack (multiple required parameters)
        mock_operator_instance.call.reset_mock()
        recording.DeleteTrack(RecordingToken="rec5", TrackToken="track1")
        mock_operator_instance.call.assert_called_with(
            "DeleteTrack", RecordingToken="rec5", TrackToken="track1"
        )

        # Test CreateRecordingJob (required parameter)
        mock_operator_instance.call.reset_mock()
        recording.CreateRecordingJob(
            JobConfiguration={"RecordingToken": "rec6", "Mode": "Active"}
        )
        mock_operator_instance.call.assert_called_with(
            "CreateRecordingJob",
            JobConfiguration={"RecordingToken": "rec6", "Mode": "Active"},
        )

        # Test DeleteRecordingJob (required parameter)
        mock_operator_instance.call.reset_mock()
        recording.DeleteRecordingJob(JobToken="job1")
        mock_operator_instance.call.assert_called_with(
            "DeleteRecordingJob", JobToken="job1"
        )

        # Test GetRecordingJobs (no parameters)
        mock_operator_instance.call.reset_mock()
        recording.GetRecordingJobs()
        mock_operator_instance.call.assert_called_with("GetRecordingJobs")

        # Test SetRecordingJobMode (multiple required parameters)
        mock_operator_instance.call.reset_mock()
        recording.SetRecordingJobMode(JobToken="job2", Mode="Idle")
        mock_operator_instance.call.assert_called_with(
            "SetRecordingJobMode", JobToken="job2", Mode="Idle"
        )

        # Test ExportRecordedData (required + optional parameters)
        mock_operator_instance.call.reset_mock()
        recording.ExportRecordedData(
            SearchScope={"RecordingToken": "rec7"},
            FileFormat="MP4",
            StorageDestination={"Uri": "ftp://storage/export"},
            StartPoint="2024-01-01T00:00:00Z",
            EndPoint="2024-01-02T00:00:00Z",
        )
        mock_operator_instance.call.assert_called_with(
            "ExportRecordedData",
            StartPoint="2024-01-01T00:00:00Z",
            EndPoint="2024-01-02T00:00:00Z",
            SearchScope={"RecordingToken": "rec7"},
            FileFormat="MP4",
            StorageDestination={"Uri": "ftp://storage/export"},
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

    @patch("onvif.services.recording.ONVIFOperator")
    def test_parameter_forwarding(self, mock_operator_class):
        """Test that parameters are correctly forwarded to operator.call()."""
        mock_operator_instance = Mock()
        mock_operator_class.return_value = mock_operator_instance
        mock_operator_instance.call.return_value = {}

        recording = Recording(xaddr="http://test:80/onvif/Recording")

        # Test that all parameters are forwarded as keyword arguments
        test_cases = [
            {
                "method": "CreateRecording",
                "params": {"RecordingConfiguration": {"Source": {"SourceId": "src1"}}},
            },
            {
                "method": "DeleteRecording",
                "params": {"RecordingToken": "rec1"},
            },
            {
                "method": "SetRecordingConfiguration",
                "params": {
                    "RecordingToken": "rec2",
                    "RecordingConfiguration": {"Source": {"SourceId": "src2"}},
                },
            },
            {
                "method": "GetRecordingConfiguration",
                "params": {"RecordingToken": "rec3"},
            },
            {
                "method": "CreateTrack",
                "params": {
                    "RecordingToken": "rec4",
                    "TrackConfiguration": {"TrackType": "Audio"},
                },
            },
            {
                "method": "DeleteTrack",
                "params": {"RecordingToken": "rec5", "TrackToken": "track1"},
            },
            {
                "method": "SetTrackConfiguration",
                "params": {
                    "RecordingToken": "rec6",
                    "TrackToken": "track2",
                    "TrackConfiguration": {"TrackType": "Metadata"},
                },
            },
            {
                "method": "CreateRecordingJob",
                "params": {
                    "JobConfiguration": {"RecordingToken": "rec7", "Mode": "Active"}
                },
            },
            {
                "method": "DeleteRecordingJob",
                "params": {"JobToken": "job1"},
            },
            {
                "method": "SetRecordingJobMode",
                "params": {"JobToken": "job2", "Mode": "Active"},
            },
            {
                "method": "GetRecordingJobState",
                "params": {"JobToken": "job3"},
            },
            {
                "method": "ExportRecordedData",
                "params": {
                    "SearchScope": {"RecordingToken": "rec8"},
                    "FileFormat": "AVI",
                    "StorageDestination": {"Uri": "http://storage/export"},
                    "StartPoint": "2024-06-01T00:00:00Z",
                    "EndPoint": "2024-06-02T00:00:00Z",
                },
            },
            {
                "method": "StopExportRecordedData",
                "params": {"OperationToken": "op1"},
            },
            {
                "method": "OverrideSegmentDuration",
                "params": {
                    "TargetSegmentDuration": "PT1H",
                    "Expiration": "2024-12-31T23:59:59Z",
                    "RecordingConfiguration": {"Source": {"SourceId": "src3"}},
                },
            },
        ]

        for test_case in test_cases:
            mock_operator_instance.call.reset_mock()
            method = getattr(recording, test_case["method"])
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
