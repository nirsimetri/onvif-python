# onvif/services/recording.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


class Recording(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 2.1 (June 2011) Split from Core 2.0
        # - RecordingBinding (ver10/recording.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/recording.wsdl

        definition = ONVIFWSDL.get_definition("recording")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Recording",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")

    def CreateRecording(self, RecordingConfiguration):
        return self.operator.call(
            "CreateRecording", RecordingConfiguration=RecordingConfiguration
        )

    def DeleteRecording(self, RecordingToken):
        return self.operator.call("DeleteRecording", RecordingToken=RecordingToken)

    def GetRecordings(self):
        return self.operator.call("GetRecordings")

    def SetRecordingConfiguration(self, RecordingToken, RecordingConfiguration):
        return self.operator.call(
            "SetRecordingConfiguration",
            RecordingToken=RecordingToken,
            RecordingConfiguration=RecordingConfiguration,
        )

    def GetRecordingConfiguration(self, RecordingToken):
        return self.operator.call(
            "GetRecordingConfiguration", RecordingToken=RecordingToken
        )

    def GetRecordingOptions(self, RecordingToken):
        return self.operator.call("GetRecordingOptions", RecordingToken=RecordingToken)

    def CreateTrack(self, RecordingToken, TrackConfiguration):
        return self.operator.call(
            "CreateTrack",
            RecordingToken=RecordingToken,
            TrackConfiguration=TrackConfiguration,
        )

    def DeleteTrack(self, RecordingToken, TrackToken):
        return self.operator.call(
            "DeleteTrack", RecordingToken=RecordingToken, TrackToken=TrackToken
        )

    def GetTrackConfiguration(self, RecordingToken, TrackToken):
        return self.operator.call(
            "GetTrackConfiguration",
            RecordingToken=RecordingToken,
            TrackToken=TrackToken,
        )

    def SetTrackConfiguration(self, RecordingToken, TrackToken, TrackConfiguration):
        return self.operator.call(
            "SetTrackConfiguration",
            RecordingToken=RecordingToken,
            TrackToken=TrackToken,
            TrackConfiguration=TrackConfiguration,
        )

    def CreateRecordingJob(self, JobConfiguration):
        return self.operator.call(
            "CreateRecordingJob", JobConfiguration=JobConfiguration
        )

    def DeleteRecordingJob(self, JobToken):
        return self.operator.call("DeleteRecordingJob", JobToken=JobToken)

    def GetRecordingJobs(self):
        return self.operator.call("GetRecordingJobs")

    def SetRecordingJobConfiguration(self, JobToken, JobConfiguration):
        return self.operator.call(
            "SetRecordingJobConfiguration",
            JobToken=JobToken,
            JobConfiguration=JobConfiguration,
        )

    def GetRecordingJobConfiguration(self, JobToken):
        return self.operator.call("GetRecordingJobConfiguration", JobToken=JobToken)

    def SetRecordingJobMode(self, JobToken, Mode):
        return self.operator.call("SetRecordingJobMode", JobToken=JobToken, Mode=Mode)

    def GetRecordingJobState(self, JobToken):
        return self.operator.call("GetRecordingJobState", JobToken=JobToken)

    def ExportRecordedData(
        self,
        SearchScope,
        FileFormat,
        StorageDestination,
        StartPoint=None,
        EndPoint=None,
    ):
        return self.operator.call(
            "ExportRecordedData",
            StartPoint=StartPoint,
            EndPoint=EndPoint,
            SearchScope=SearchScope,
            FileFormat=FileFormat,
            StorageDestination=StorageDestination,
        )

    def StopExportRecordedData(self, OperationToken):
        return self.operator.call(
            "StopExportRecordedData", OperationToken=OperationToken
        )

    def GetExportRecordedDataState(self, OperationToken):
        return self.operator.call(
            "GetExportRecordedDataState", OperationToken=OperationToken
        )

    def OverrideSegmentDuration(
        self, TargetSegmentDuration, Expiration, RecordingConfiguration
    ):
        return self.operator.call(
            "OverrideSegmentDuration",
            TargetSegmentDuration=TargetSegmentDuration,
            Expiration=Expiration,
            RecordingConfiguration=RecordingConfiguration,
        )
