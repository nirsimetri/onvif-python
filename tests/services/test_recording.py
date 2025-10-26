from onvif.services import Recording
from base_service_test import ONVIFServiceTestBase


class TestRecordingWSDLCompliance(ONVIFServiceTestBase):
    """Test that Recording service implementation matches WSDL specification."""

    # Service configuration
    SERVICE_CLASS = Recording
    SERVICE_NAME = "recording"
    WSDL_PATH_COMPONENTS = ["ver10", "recording.wsdl"]
    BINDING_NAME = "RecordingBinding"
    NAMESPACE_PREFIX = "trc"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/recording/wsdl"
    XADDR_PATH = "/onvif/Recording"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetServiceCapabilities", "params": {}},
            {"method": "GetRecordings", "params": {}},
            {
                "method": "CreateRecording",
                "params": {
                    "RecordingConfiguration": {"Source": {"SourceId": "source1"}}
                },
            },
            {"method": "DeleteRecording", "params": {"RecordingToken": "rec1"}},
            {
                "method": "SetRecordingConfiguration",
                "params": {
                    "RecordingToken": "rec2",
                    "RecordingConfiguration": {"Source": {"SourceId": "source2"}},
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
                    "TrackConfiguration": {"TrackType": "Video"},
                },
            },
            {
                "method": "DeleteTrack",
                "params": {"RecordingToken": "rec5", "TrackToken": "track1"},
            },
            {
                "method": "CreateRecordingJob",
                "params": {
                    "JobConfiguration": {"RecordingToken": "rec6", "Mode": "Active"}
                },
            },
            {"method": "DeleteRecordingJob", "params": {"JobToken": "job1"}},
            {"method": "GetRecordingJobs", "params": {}},
            {
                "method": "SetRecordingJobMode",
                "params": {"JobToken": "job2", "Mode": "Idle"},
            },
            {
                "method": "ExportRecordedData",
                "params": {
                    "StartPoint": "2024-01-01T00:00:00Z",
                    "EndPoint": "2024-01-02T00:00:00Z",
                    "SearchScope": {"RecordingToken": "rec7"},
                    "FileFormat": "MP4",
                    "StorageDestination": {"Uri": "ftp://storage/export"},
                },
            },
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
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
        self.run_parameter_forwarding_tests(test_cases)
