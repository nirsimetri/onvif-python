# onvif/services/accesscontrol.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


class AccessControl(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 2.3 (May 2013) Release Notes
        # - PACSBinding (ver10/pacs/accesscontrol.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/pacs/accesscontrol.wsdl

        definition = ONVIFWSDL.get_definition("accesscontrol")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="AccessControl",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")

    def GetAccessPointInfoList(self, Limit=None, StartReference=None):
        return self.operator.call(
            "GetAccessPointInfoList", Limit=Limit, StartReference=StartReference
        )

    def GetAccessPointInfo(self, Token):
        return self.operator.call("GetAccessPointInfo", Token=Token)

    def GetAccessPointList(self, Limit=None, StartReference=None):
        return self.operator.call(
            "GetAccessPointList", Limit=Limit, StartReference=StartReference
        )

    def GetAccessPoints(self, Token):
        return self.operator.call("GetAccessPoints", Token=Token)

    def CreateAccessPoint(self, AccessPoint):
        return self.operator.call("CreateAccessPoint", AccessPoint=AccessPoint)

    def SetAccessPoint(self, AccessPoint):
        return self.operator.call("SetAccessPoint", AccessPoint=AccessPoint)

    def ModifyAccessPoint(self, AccessPoint):
        return self.operator.call("ModifyAccessPoint", AccessPoint=AccessPoint)

    def DeleteAccessPoint(self, Token):
        return self.operator.call("DeleteAccessPoint", Token=Token)

    def SetAccessPointAuthenticationProfile(self, Token, AuthenticationProfileToken):
        return self.operator.call(
            "SetAccessPointAuthenticationProfile",
            Token=Token,
            AuthenticationProfileToken=AuthenticationProfileToken,
        )

    def DeleteAccessPointAuthenticationProfile(self, Token):
        return self.operator.call("DeleteAccessPointAuthenticationProfile", Token=Token)

    def GetAreaInfoList(self, Limit=None, StartReference=None):
        return self.operator.call(
            "GetAreaInfoList", Limit=Limit, StartReference=StartReference
        )

    def GetAreaInfo(self, Token):
        return self.operator.call("GetAreaInfo", Token=Token)

    def GetAreaList(self, Limit=None, StartReference=None):
        return self.operator.call(
            "GetAreaList", Limit=Limit, StartReference=StartReference
        )

    def GetAreas(self, Token):
        return self.operator.call("GetAreas", Token=Token)

    def CreateArea(self, Area):
        return self.operator.call("CreateArea", Area=Area)

    def SetArea(self, Area):
        return self.operator.call("SetArea", Area=Area)

    def ModifyArea(self, Area):
        return self.operator.call("ModifyArea", Area=Area)

    def DeleteArea(self, Token):
        return self.operator.call("DeleteArea", Token=Token)

    def GetAccessPointState(self, Token):
        return self.operator.call("GetAccessPointState", Token=Token)

    def EnableAccessPoint(self, Token):
        return self.operator.call("EnableAccessPoint", Token=Token)

    def DisableAccessPoint(self, Token):
        return self.operator.call("DisableAccessPoint", Token=Token)

    def Feedback(
        self, AccessPointToken, FeedbackType, RecognitionType=None, TextMessage=None
    ):
        return self.operator.call(
            "Feedback",
            AccessPointToken=AccessPointToken,
            FeedbackType=FeedbackType,
            RecognitionType=RecognitionType,
            TextMessage=TextMessage,
        )

    def ExternalAuthorization(
        self, AccessPointToken, Decision, CredentialToken=None, Reason=None
    ):
        return self.operator.call(
            "ExternalAuthorization",
            AccessPointToken=AccessPointToken,
            CredentialToken=CredentialToken,
            Reason=Reason,
            Decision=Decision,
        )
