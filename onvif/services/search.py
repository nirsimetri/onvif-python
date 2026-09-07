"""Search service implementation."""

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class Search(ONVIFService):
    """Search service client.

    References:
    - First introduced: ONVIF Release 2.1 (June 2011) Split from Core 2.0
    - Binding name: `SearchBinding` (ver10/search.wsdl)
    - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/search.wsdl
    - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/RecordingSearch.xml
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("search")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="SearchRecording",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """Returns the capabilities of the search service.

        The result is returned in a typed answer.
        """
        return self.operator.call("GetServiceCapabilities")

    def GetRecordingSummary(self):
        """GetRecordingSummary is used to get a summary description of all recorded
        data.

        This operation is mandatory to support for a device implementing the recording
        search service.
        """
        return self.operator.call("GetRecordingSummary")

    def GetRecordingInformation(self, RecordingToken):
        """Returns information about a single Recording specified by a RecordingToken.

        This operation is mandatory to support for a device implementing the recording
        search service.
        """
        return self.operator.call(
            "GetRecordingInformation", RecordingToken=RecordingToken
        )

    def GetMediaAttributes(self, Time, RecordingTokens=None):
        """Returns a set of media attributes for all tracks of the specified recordings
        at a specified point in time.

        Clients using this operation shall be able to use it as a non blocking
        operation. A device shall set the starttime and endtime of the MediaAttributes
        structure to equal values if calculating this range would causes this operation
        to block. See MediaAttributes structure for more information. This operation is
        mandatory to support for a device implementing the recording search service.
        """
        return self.operator.call(
            "GetMediaAttributes", RecordingTokens=RecordingTokens, Time=Time
        )

    def FindRecordings(self, Scope, KeepAliveTime, MaxMatches=None):
        """FindRecordings starts a search session, looking for recordings that matches
        the scope (See 20.2.4) defined in the request.

        Results from the search are acquired using the GetRecordingSearchResults
        request, specifying the search token returned from this request. The device
        shall continue searching until one of the following occurs:

        - The entire time range from StartPoint to EndPoint has been searched through.
        - The total number of matches has been found, defined by the MaxMatches parameter.
        - The session has been ended by a client EndSession request.
        - The session has been ended because KeepAliveTime since the last request related
        to this session has expired.

        The order of the results is undefined, to allow the device to return results in
        any order they are found. This operation is mandatory to support for a device
        implementing the recording search service.
        """
        return self.operator.call(
            "FindRecordings",
            Scope=Scope,
            MaxMatches=MaxMatches,
            KeepAliveTime=KeepAliveTime,
        )

    def GetRecordingSearchResults(
        self, SearchToken, MinResults=None, MaxResults=None, WaitTime=None
    ):
        """GetRecordingSearchResults acquires the results from a recording search
        session previously initiated by a FindRecordings operation.

        The response shall not include results already returned in previous requests for
        the same session. If MaxResults is specified, the response shall not contain
        more than MaxResults results. The number of results relates to the number of
        recordings. For viewing individual recorded data for a signal track use the
        FindEvents method.

        GetRecordingSearchResults shall block until:
        - MaxResults results are available for the response if MaxResults is specified.
        - MinResults results are available for the response if MinResults is specified.
        - WaitTime has expired.
        - Search is completed or stopped.

        This operation is mandatory to support for a device implementing the recording
        search service.
        """
        return self.operator.call(
            "GetRecordingSearchResults",
            SearchToken=SearchToken,
            MinResults=MinResults,
            MaxResults=MaxResults,
            WaitTime=WaitTime,
        )

    def FindEvents(
        self,
        StartPoint,
        Scope,
        SearchFilter,
        IncludeStartState,
        KeepAliveTime,
        EndPoint=None,
        MaxMatches=None,
    ):
        """FindEvents starts a search session, looking for recording events (in the
        scope that matches the search filter defined in the request.

        Results from the search are acquired using the GetEventSearchResults request,
        specifying the search token returned from this request.

        The device shall continue searching until one of the following occurs:
        - The entire time range from StartPoint to EndPoint has been searched through.
        - The total number of matches has been found, defined by the MaxMatches parameter.
        - The session has been ended by a client EndSession request.
        - The session has been ended because KeepAliveTime since the last request related
        to this session has expired.

        Results shall be ordered by time, ascending in case of forward search, or
        descending in case of backward search. This operation is mandatory to support
        for a device implementing the recording search service.
        """
        return self.operator.call(
            "FindEvents",
            StartPoint=StartPoint,
            EndPoint=EndPoint,
            Scope=Scope,
            SearchFilter=SearchFilter,
            IncludeStartState=IncludeStartState,
            MaxMatches=MaxMatches,
            KeepAliveTime=KeepAliveTime,
        )

    def GetEventSearchResults(
        self, SearchToken, MinResults=None, MaxResults=None, WaitTime=None
    ):
        """GetEventSearchResults acquires the results from a recording event search
        session previously initiated by a FindEvents operation.

        The response shall not include results already returned in previous requests for
        the same session. If MaxResults is specified, the response shall not contain
        more than MaxResults results.

        GetEventSearchResults shall block until:
        - MaxResults results are available for the response if MaxResults is specified.
        - MinResults results are available for the response if MinResults is specified.
        - WaitTime has expired.
        - Search is completed or stopped.

        This operation is mandatory to support for a device implementing the recording
        search service.
        """
        return self.operator.call(
            "GetEventSearchResults",
            SearchToken=SearchToken,
            MinResults=MinResults,
            MaxResults=MaxResults,
            WaitTime=WaitTime,
        )

    def FindPTZPosition(
        self,
        StartPoint,
        Scope,
        SearchFilter,
        KeepAliveTime,
        EndPoint=None,
        MaxMatches=None,
    ):
        """FindPTZPosition starts a search session, looking for ptz positions in the
        scope (See 20.2.4) that matches the search filter defined in the request.

        Results from the search are acquired using the GetPTZPositionSearchResults
        request, specifying the search token returned from this request.

        The device shall continue searching until one of the following occurs:
        - The entire time range from StartPoint to EndPoint has been searched through.
        - The total number of matches has been found, defined by the MaxMatches parameter.
        - The session has been ended by a client EndSession request.
        - The session has been ended because KeepAliveTime since the last request related
        to this session has expired.

        This operation is mandatory to support whenever CanContainPTZ is true for any
        metadata track in any recording on the device.
        """
        return self.operator.call(
            "FindPTZPosition",
            StartPoint=StartPoint,
            EndPoint=EndPoint,
            Scope=Scope,
            SearchFilter=SearchFilter,
            MaxMatches=MaxMatches,
            KeepAliveTime=KeepAliveTime,
        )

    def GetPTZPositionSearchResults(
        self, SearchToken, MinResults=None, MaxResults=None, WaitTime=None
    ):
        """GetPTZPositionSearchResults acquires the results from a ptz position search
        session previously initiated by a FindPTZPosition operation.

        The response shall not include results already returned in previous requests for
        the same session. If MaxResults is specified, the response shall not contain
        more than MaxResults results.

        GetPTZPositionSearchResults shall block until:
        - MaxResults results are available for the response if MaxResults is specified.
        - MinResults results are available for the response if MinResults is specified.
        - WaitTime has expired.
        - Search is completed or stopped.

        This operation is mandatory to support whenever CanContainPTZ is true for any
        metadata track in any recording on the device.
        """
        return self.operator.call(
            "GetPTZPositionSearchResults",
            SearchToken=SearchToken,
            MinResults=MinResults,
            MaxResults=MaxResults,
            WaitTime=WaitTime,
        )

    def GetSearchState(self, SearchToken):
        """GetSearchState returns the current state of the specified search session.

        This command is deprecated .
        """
        return self.operator.call("GetSearchState", SearchToken=SearchToken)

    def EndSearch(self, SearchToken):
        """EndSearch stops and ongoing search session, causing any blocking result
        request to return and the SearchToken to become invalid.

        If the search was interrupted before completion, the point in time that the
        search had reached shall be returned. If the search had not yet begun, the
        StartPoint shall be returned. If the search was completed the original EndPoint
        supplied by the Find operation shall be returned. When issuing EndSearch on a
        FindRecordings request the EndPoint is undefined and shall not be used since the
        FindRecordings request doesn't have StartPoint/EndPoint. This operation is
        mandatory to support for a device implementing the recording search service.
        """
        return self.operator.call("EndSearch", SearchToken=SearchToken)

    def FindMetadata(
        self,
        StartPoint,
        Scope,
        MetadataFilter,
        KeepAliveTime,
        EndPoint=None,
        MaxMatches=None,
    ):
        """FindMetadata starts a search session, looking for metadata in the scope (See
        20.2.4) that matches the search filter defined in the request.

        Results from the search are acquired using the GetMetadataSearchResults request,
        specifying the search token returned from this request.

        The device shall continue searching until one of the following occurs:
        - The entire time range from StartPoint to EndPoint has been searched through.
        - The total number of matches has been found, defined by the MaxMatches parameter.
        - The session has been ended by a client EndSession request.
        - The session has been ended because KeepAliveTime since the last request related
        to this session has expired.

        This operation is mandatory to support if the MetaDataSearch capability is set
        to true in the SearchCapabilities structure return by the GetCapabilities
        command in the Device service.
        """
        return self.operator.call(
            "FindMetadata",
            StartPoint=StartPoint,
            EndPoint=EndPoint,
            Scope=Scope,
            MetadataFilter=MetadataFilter,
            MaxMatches=MaxMatches,
            KeepAliveTime=KeepAliveTime,
        )

    def GetMetadataSearchResults(
        self, SearchToken, MinResults=None, MaxResults=None, WaitTime=None
    ):
        """GetMetadataSearchResults acquires the results from a recording search session
        previously initiated by a FindMetadata operation.

        The response shall not include results already returned in previous requests for
        the same session. If MaxResults is specified, the response shall not contain
        more than MaxResults results.

        GetMetadataSearchResults shall block until:
        - MaxResults results are available for the response if MaxResults is specified.
        - MinResults results are available for the response if MinResults is specified.
        - WaitTime has expired.
        - Search is completed or stopped.

        This operation is mandatory to support if the MetaDataSearch capability is set
        to true in the SearchCapabilities structure return by the GetCapabilities
        command in the Device service.
        """
        return self.operator.call(
            "GetMetadataSearchResults",
            SearchToken=SearchToken,
            MinResults=MinResults,
            MaxResults=MaxResults,
            WaitTime=WaitTime,
        )

    def SearchImageByNL(
        self,
        StartPoint,
        Text,
        KeepAliveTime,
        EndPoint=None,
        RecordingToken=None,
        Similarity=None,
        MaxMatches=None,
    ):
        """Starts a natural language search session and specifies the search
        parameters."""
        return self.operator.call(
            "SearchImageByNL",
            StartPoint=StartPoint,
            EndPoint=EndPoint,
            RecordingToken=RecordingToken,
            Text=Text,
            Similarity=Similarity,
            MaxMatches=MaxMatches,
            KeepAliveTime=KeepAliveTime,
        )

    def GetNLSearchResults(
        self, SearchToken, MinResults=None, MaxResults=None, WaitTime=None
    ):
        """Gets results from a natural language search session."""
        return self.operator.call(
            "GetNLSearchResults",
            SearchToken=SearchToken,
            MinResults=MinResults,
            MaxResults=MaxResults,
            WaitTime=WaitTime,
        )

    def SearchImageByImage(
        self,
        StartPoint,
        KeepAliveTime,
        EndPoint=None,
        RecordingToken=None,
        TargetImageURI=None,
        TargetImageData=None,
        MaxMatches=None,
    ):
        """Starts an image-based search session and specifies the search parameters."""
        return self.operator.call(
            "SearchImageByImage",
            StartPoint=StartPoint,
            EndPoint=EndPoint,
            RecordingToken=RecordingToken,
            TargetImageURI=TargetImageURI,
            TargetImageData=TargetImageData,
            MaxMatches=MaxMatches,
            KeepAliveTime=KeepAliveTime,
        )

    def GetImageSearchResults(
        self, SearchToken, MinResults=None, MaxResults=None, WaitTime=None
    ):
        """Gets results from an image-based search session."""
        return self.operator.call(
            "GetImageSearchResults",
            SearchToken=SearchToken,
            MinResults=MinResults,
            MaxResults=MaxResults,
            WaitTime=WaitTime,
        )
