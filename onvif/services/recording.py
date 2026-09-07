"""Recording service implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name,too-many-public-methods
class Recording(ONVIFService):
    """Recording service client.

    References:
    - First introduced: ONVIF Release 2.1 (June 2011) Split from Core 2.0
    - Binding name: `RecordingBinding` (ver10/recording.wsdl)
    - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/recording.wsdl
    - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/RecordingControl.xml
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("recording")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Recording",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """Returns the capabilities of the recording service.

        The result is returned in a typed answer.
        """
        return self.operator.call("GetServiceCapabilities")

    def CreateRecording(self, RecordingConfiguration):
        """CreateRecording shall create a new recording.

        The new recording shall be created with a track for each supported TrackType see
        Recording Control Spec.

        This method is optional. It shall be available if the
        Recording/DynamicRecordings capability is TRUE.

        When successfully completed, CreateRecording shall have created three tracks
        with the following configurations:

        - TrackToken TrackType
        - VIDEO001 Video
        - AUDIO001 Audio
        - META001 Metadata

        All tracks created as response to a CreateRecording request shall have the
        MaximumRetentionTime set to 0 (unlimited), and the Description set to the empty
        string, by default.
        """
        return self.operator.call(
            "CreateRecording", RecordingConfiguration=RecordingConfiguration
        )

    def DeleteRecording(self, RecordingToken):
        """DeleteRecording shall delete a recording object.

        Whenever a recording is deleted, the device shall delete all the tracks that are
        part of the recording, and it shall delete all the Recording Jobs that record
        into the recording. For each deleted recording job, the device shall also delete
        all the receiver objects associated with the recording job that are
        automatically created using the AutoCreateReceiver field of the recording job
        configuration structure and are not used in any other recording job.

        This method is optional. It shall be available if the
        Recording/DynamicRecordings capability is TRUE.
        """
        return self.operator.call("DeleteRecording", RecordingToken=RecordingToken)

    def GetRecordings(self):
        """GetRecordings shall return a description of all the recordings in the device.

        This description shall include a list of all the tracks for each recording.
        """
        return self.operator.call("GetRecordings")

    def SetRecordingConfiguration(self, RecordingToken, RecordingConfiguration):
        """SetRecordingConfiguration shall change the configuration of a recording."""
        return self.operator.call(
            "SetRecordingConfiguration",
            RecordingToken=RecordingToken,
            RecordingConfiguration=RecordingConfiguration,
        )

    def GetRecordingConfiguration(self, RecordingToken):
        """GetRecordingConfiguration shall retrieve the recording configuration for a
        recording."""
        return self.operator.call(
            "GetRecordingConfiguration", RecordingToken=RecordingToken
        )

    def GetRecordingOptions(self, RecordingToken):
        """GetRecordingOptions returns information for a recording identified by the
        RecordingToken.

        The information includes the number of additonal tracks as well as recording
        jobs that can be configured.
        """
        return self.operator.call("GetRecordingOptions", RecordingToken=RecordingToken)

    def CreateTrack(self, RecordingToken, TrackConfiguration):
        """This method shall create a new track within a recording.

        This method is optional. It shall be available if the Recording/DynamicTracks
        capability is TRUE.

        A TrackToken in itself does not uniquely identify a specific track. Tracks
        within different recordings may have the same TrackToken.
        """
        return self.operator.call(
            "CreateTrack",
            RecordingToken=RecordingToken,
            TrackConfiguration=TrackConfiguration,
        )

    def DeleteTrack(self, RecordingToken, TrackToken):
        """DeleteTrack shall remove a track from a recording.

        All the data in the track shall be deleted.

        This method is optional. It shall be available if the Recording/DynamicTracks
        capability is TRUE.
        """
        return self.operator.call(
            "DeleteTrack", RecordingToken=RecordingToken, TrackToken=TrackToken
        )

    def GetTrackConfiguration(self, RecordingToken, TrackToken):
        """GetTrackConfiguration shall retrieve the configuration for a specific
        track."""
        return self.operator.call(
            "GetTrackConfiguration",
            RecordingToken=RecordingToken,
            TrackToken=TrackToken,
        )

    def SetTrackConfiguration(self, RecordingToken, TrackToken, TrackConfiguration):
        """SetTrackConfiguration shall change the configuration of a track."""
        return self.operator.call(
            "SetTrackConfiguration",
            RecordingToken=RecordingToken,
            TrackToken=TrackToken,
            TrackConfiguration=TrackConfiguration,
        )

    def CreateRecordingJob(self, JobConfiguration):
        """CreateRecordingJob shall create a new recording job.

        The JobConfiguration returned from CreateRecordingJob shall be identical to the
        JobConfiguration passed into CreateRecordingJob, except for the ReceiverToken
        and the AutoCreateReceiver. In the returned structure, the ReceiverToken shall
        be present and valid and the AutoCreateReceiver field shall be omitted.
        """
        return self.operator.call(
            "CreateRecordingJob", JobConfiguration=JobConfiguration
        )

    def DeleteRecordingJob(self, JobToken):
        """DeleteRecordingJob removes a recording job.

        It shall also implicitly delete all the receiver objects associated with the
        recording job that are automatically created using the AutoCreateReceiver field
        of the recording job configuration structure and are not used in any other
        recording job.
        """
        return self.operator.call("DeleteRecordingJob", JobToken=JobToken)

    def GetRecordingJobs(self):
        """GetRecordingJobs shall return a list of all the recording jobs in the
        device."""
        return self.operator.call("GetRecordingJobs")

    def SetRecordingJobConfiguration(self, JobToken, JobConfiguration):
        """SetRecordingJobConfiguration shall change the configuration for a recording
        job.

        SetRecordingJobConfiguration shall implicitly delete any receiver objects that
        were created automatically if they are no longer used as a result of changing
        the recording job configuration.
        """
        return self.operator.call(
            "SetRecordingJobConfiguration",
            JobToken=JobToken,
            JobConfiguration=JobConfiguration,
        )

    def GetRecordingJobConfiguration(self, JobToken):
        """GetRecordingJobConfiguration shall return the current configuration for a
        recording job."""
        return self.operator.call("GetRecordingJobConfiguration", JobToken=JobToken)

    def SetRecordingJobMode(self, JobToken, Mode):
        """SetRecordingJobMode shall change the mode of the recording job.

        Using this method shall be equivalent to retrieving the recording job
        configuration, and writing it back with a different mode.
        """
        return self.operator.call("SetRecordingJobMode", JobToken=JobToken, Mode=Mode)

    def GetRecordingJobState(self, JobToken):
        """GetRecordingJobState returns the state of a recording job.

        It includes an aggregated state, and state for each track of the recording job.
        """
        return self.operator.call("GetRecordingJobState", JobToken=JobToken)

    def ExportRecordedData(
        self,
        SearchScope,
        FileFormat,
        StorageDestination,
        StartPoint=None,
        EndPoint=None,
    ):
        """Exports the selected recordings (from existing recorded data) to the given
        storage target based on the requested file format."""
        return self.operator.call(
            "ExportRecordedData",
            StartPoint=StartPoint,
            EndPoint=EndPoint,
            SearchScope=SearchScope,
            FileFormat=FileFormat,
            StorageDestination=StorageDestination,
        )

    def StopExportRecordedData(self, OperationToken):
        """Stops the selected ExportRecordedData operation."""
        return self.operator.call(
            "StopExportRecordedData", OperationToken=OperationToken
        )

    def GetExportRecordedDataState(self, OperationToken):
        """Retrieves the status of selected ExportRecordedData operation."""
        return self.operator.call(
            "GetExportRecordedDataState", OperationToken=OperationToken
        )

    def OverrideSegmentDuration(
        self, TargetSegmentDuration, Expiration, RecordingConfiguration
    ):
        """Requests a temporary override of the target segment duration for a recording
        configuration."""
        return self.operator.call(
            "OverrideSegmentDuration",
            TargetSegmentDuration=TargetSegmentDuration,
            Expiration=Expiration,
            RecordingConfiguration=RecordingConfiguration,
        )

    def ListRecordedSegments(self, Time, RecordingToken, MaxResults=None):
        """Lists available recorded segments related to the specified RecordingToken."""
        return self.operator.call(
            "ListRecordedSegments",
            Time=Time,
            RecordingToken=RecordingToken,
            MaxResults=MaxResults,
        )

    def ExportRecordedSegments(
        self,
        Time,
        RecordingToken,
        Alias=None,
        StorageToken=None,
        Track=None,
    ):
        """Exports the selected recorded segments (from existing recorded data) to the
        storage attached to the given recording configuration."""
        return self.operator.call(
            "ExportRecordedSegments",
            Time=Time,
            RecordingToken=RecordingToken,
            Alias=Alias,
            StorageToken=StorageToken,
            Track=Track,
        )

    def StopExportRecordedSegments(self, OperationToken):
        """Stops the selected ExportRecordedSegments operation."""
        return self.operator.call(
            "StopExportRecordedSegments", OperationToken=OperationToken
        )
