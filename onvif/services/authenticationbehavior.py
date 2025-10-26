# onvif/services/authenticationbehavior.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


class AuthenticationBehavior(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 18.06 (June 2018) Release Notes
        # - AuthenticationBehaviorBinding (ver10/authenticationbehavior/wsdl/authenticationbehavior.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/authenticationbehavior/wsdl/authenticationbehavior.wsdl

        definition = ONVIFWSDL.get_definition("authenticationbehavior")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="AuthenticationBehavior",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")

    def GetAuthenticationProfileInfo(self, Token):
        return self.operator.call("GetAuthenticationProfileInfo", Token=Token)

    def GetAuthenticationProfileInfoList(self, Limit=None, StartReference=None):
        return self.operator.call(
            "GetAuthenticationProfileInfoList",
            Limit=Limit,
            StartReference=StartReference,
        )

    def GetAuthenticationProfiles(self, Token):
        return self.operator.call("GetAuthenticationProfiles", Token=Token)

    def GetAuthenticationProfileList(self, Limit=None, StartReference=None):
        return self.operator.call(
            "GetAuthenticationProfileList", Limit=Limit, StartReference=StartReference
        )

    def CreateAuthenticationProfile(self, AuthenticationProfile):
        return self.operator.call(
            "CreateAuthenticationProfile", AuthenticationProfile=AuthenticationProfile
        )

    def SetAuthenticationProfile(self, AuthenticationProfile):
        return self.operator.call(
            "SetAuthenticationProfile", AuthenticationProfile=AuthenticationProfile
        )

    def ModifyAuthenticationProfile(self, AuthenticationProfile):
        return self.operator.call(
            "ModifyAuthenticationProfile", AuthenticationProfile=AuthenticationProfile
        )

    def DeleteAuthenticationProfile(self, Token):
        return self.operator.call("DeleteAuthenticationProfile", Token=Token)

    def GetSecurityLevelInfo(self, Token):
        return self.operator.call("GetSecurityLevelInfo", Token=Token)

    def GetSecurityLevelInfoList(self, Limit=None, StartReference=None):
        return self.operator.call(
            "GetSecurityLevelInfoList", Limit=Limit, StartReference=StartReference
        )

    def GetSecurityLevels(self, Token):
        return self.operator.call("GetSecurityLevels", Token=Token)

    def GetSecurityLevelList(self, Limit=None, StartReference=None):
        return self.operator.call(
            "GetSecurityLevelList", Limit=Limit, StartReference=StartReference
        )

    def CreateSecurityLevel(self, SecurityLevel):
        return self.operator.call("CreateSecurityLevel", SecurityLevel=SecurityLevel)

    def SetSecurityLevel(self, SecurityLevel):
        return self.operator.call("SetSecurityLevel", SecurityLevel=SecurityLevel)

    def ModifySecurityLevel(self, SecurityLevel):
        return self.operator.call("ModifySecurityLevel", SecurityLevel=SecurityLevel)

    def DeleteSecurityLevel(self, Token):
        return self.operator.call("DeleteSecurityLevel", Token=Token)
