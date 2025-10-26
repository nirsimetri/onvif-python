# onvif/services/credential.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


class Credential(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 2.6 (June 2015) Release Notes
        # - CredentialBinding (ver10/credential/wsdl/credential.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/credential/wsdl/credential.wsdl

        definition = ONVIFWSDL.get_definition("credential")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Credential",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")

    def GetSupportedFormatTypes(self, CredentialIdentifierTypeName):
        return self.operator.call(
            "GetSupportedFormatTypes",
            CredentialIdentifierTypeName=CredentialIdentifierTypeName,
        )

    def GetCredentialInfo(self, Token):
        return self.operator.call("GetCredentialInfo", Token=Token)

    def GetCredentialInfoList(self, Limit=None, StartReference=None):
        return self.operator.call(
            "GetCredentialInfoList", Limit=Limit, StartReference=StartReference
        )

    def GetCredentials(self, Token):
        return self.operator.call("GetCredentials", Token=Token)

    def GetCredentialList(self, Limit=None, StartReference=None):
        return self.operator.call(
            "GetCredentialList", Limit=Limit, StartReference=StartReference
        )

    def CreateCredential(self, Credential, State):
        return self.operator.call(
            "CreateCredential", Credential=Credential, State=State
        )

    def SetCredential(self, CredentialData):
        return self.operator.call("SetCredential", CredentialData=CredentialData)

    def ModifyCredential(self, Credential):
        return self.operator.call("ModifyCredential", Credential=Credential)

    def DeleteCredential(self, Token):
        return self.operator.call("DeleteCredential", Token=Token)

    def GetCredentialState(self, Token):
        return self.operator.call("GetCredentialState", Token=Token)

    def EnableCredential(self, Token, Reason=None):
        return self.operator.call("EnableCredential", Token=Token, Reason=Reason)

    def DisableCredential(self, Token, Reason=None):
        return self.operator.call("DisableCredential", Token=Token, Reason=Reason)

    def ResetAntipassbackViolation(self, CredentialToken):
        return self.operator.call(
            "ResetAntipassbackViolation", CredentialToken=CredentialToken
        )

    def GetCredentialIdentifiers(self, CredentialToken):
        return self.operator.call(
            "GetCredentialIdentifiers", CredentialToken=CredentialToken
        )

    def SetCredentialIdentifier(self, CredentialToken, CredentialIdentifier):
        return self.operator.call(
            "SetCredentialIdentifier",
            CredentialToken=CredentialToken,
            CredentialIdentifier=CredentialIdentifier,
        )

    def DeleteCredentialIdentifier(self, CredentialToken, CredentialIdentifierTypeName):
        return self.operator.call(
            "DeleteCredentialIdentifier",
            CredentialToken=CredentialToken,
            CredentialIdentifierTypeName=CredentialIdentifierTypeName,
        )

    def GetCredentialAccessProfiles(self, CredentialToken):
        return self.operator.call(
            "GetCredentialAccessProfiles", CredentialToken=CredentialToken
        )

    def SetCredentialAccessProfiles(self, CredentialToken, CredentialAccessProfile):
        return self.operator.call(
            "SetCredentialAccessProfiles",
            CredentialToken=CredentialToken,
            CredentialAccessProfile=CredentialAccessProfile,
        )

    def DeleteCredentialAccessProfiles(self, CredentialToken, AccessProfileToken):
        return self.operator.call(
            "DeleteCredentialAccessProfiles",
            CredentialToken=CredentialToken,
            AccessProfileToken=AccessProfileToken,
        )

    def GetWhitelist(
        self,
        Limit=None,
        StartReference=None,
        IdentifierType=None,
        FormatType=None,
        Value=None,
    ):
        return self.operator.call(
            "GetWhitelist",
            Limit=Limit,
            StartReference=StartReference,
            IdentifierType=IdentifierType,
            FormatType=FormatType,
            Value=Value,
        )

    def AddToWhitelist(self, Identifier):
        return self.operator.call("AddToWhitelist", Identifier=Identifier)

    def RemoveFromWhitelist(self, Identifier):
        return self.operator.call("RemoveFromWhitelist", Identifier=Identifier)

    def DeleteWhitelist(self):
        return self.operator.call("DeleteWhitelist")

    def GetBlacklist(
        self,
        Limit=None,
        StartReference=None,
        IdentifierType=None,
        FormatType=None,
        Value=None,
    ):
        return self.operator.call(
            "GetBlacklist",
            Limit=Limit,
            StartReference=StartReference,
            IdentifierType=IdentifierType,
            FormatType=FormatType,
            Value=Value,
        )

    def AddToBlacklist(self, Identifier):
        return self.operator.call("AddToBlacklist", Identifier=Identifier)

    def RemoveFromBlacklist(self, Identifier):
        return self.operator.call("RemoveFromBlacklist", Identifier=Identifier)

    def DeleteBlacklist(self):
        return self.operator.call("DeleteBlacklist")
