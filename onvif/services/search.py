# onvif/services/search.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL


class Search:
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
        return self.operator.call("GetServiceCapabilities")

    def GetRecordingSummary(self):
        return self.operator.call("GetRecordingSummary")

    def GetRecordingInformation(self, RecordingToken):
        return self.operator.call(
            "GetRecordingInformation", RecordingToken=RecordingToken
        )

    def GetMediaAttributes(self, Time, RecordingTokens=None):
        return self.operator.call(
            "GetMediaAttributes", RecordingTokens=RecordingTokens, Time=Time
        )

    def FindRecordings(self, Scope, KeepAliveTime, MaxMatches=None):
        return self.operator.call(
            "FindRecordings",
            Scope=Scope,
            MaxMatches=MaxMatches,
            KeepAliveTime=KeepAliveTime,
        )

    def GetRecordingSearchResults(
        self, SearchToken, MinResults=None, MaxResults=None, WaitTime=None
    ):
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
        return self.operator.call(
            "GetPTZPositionSearchResults",
            SearchToken=SearchToken,
            MinResults=MinResults,
            MaxResults=MaxResults,
            WaitTime=WaitTime,
        )

    def GetSearchState(self, SearchToken):
        return self.operator.call("GetSearchState", SearchToken=SearchToken)

    def EndSearch(self, SearchToken):
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
        return self.operator.call(
            "GetMetadataSearchResults",
            SearchToken=SearchToken,
            MinResults=MinResults,
            MaxResults=MaxResults,
            WaitTime=WaitTime,
        )
