"""Credential service implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name,too-many-public-methods
class Credential(ONVIFService):
    """Credential service client.

    References:
        - First introduced: ONVIF Release 2.6 (June 2015)
        - Binding name: `CredentialBinding` (ver10/credential/wsdl/credential.wsdl)
        - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/credential/wsdl/credential.wsdl
        - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/Credential.xml
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("credential")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Credential",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """This operation returns the capabilities of the credential service."""
        return self.operator.call("GetServiceCapabilities")

    def GetSupportedFormatTypes(self, CredentialIdentifierTypeName):
        """This method returns all the supported format types of a specified identifier
        type that is supported by the device."""
        return self.operator.call(
            "GetSupportedFormatTypes",
            CredentialIdentifierTypeName=CredentialIdentifierTypeName,
        )

    def GetCredentialInfo(self, Token):
        """This operation requests a list of CredentialInfo items matching the given
        tokens.

        The device shall ignore tokens it cannot resolve and shall return an empty list
        if there are no items matching the specified tokens. The device shall not return
        a fault in this case. If the number of requested items is greater than MaxLimit,
        a TooManyItems fault shall be returned.
        """
        return self.operator.call("GetCredentialInfo", Token=Token)

    def GetCredentialInfoList(self, Limit=None, StartReference=None):
        """This operation requests a list of all CredentialInfo items provided by the
        device.

        A call to this method shall return a StartReference when not all data is
        returned and more data is available. The reference shall be valid for retrieving
        the next set of data. Please refer to section 4.8.3 in [ONVIF Access Control
        Service Specification] for more details. The number of items returned shall not
        be greater than the Limit parameter.
        """
        return self.operator.call(
            "GetCredentialInfoList", Limit=Limit, StartReference=StartReference
        )

    def GetCredentials(self, Token):
        """This operation returns the specified credential items matching the given
        tokens.

        The device shall ignore tokens it cannot resolve and shall return an empty list
        if there are no items matching specified tokens. The device shall not return a
        fault in this case. If the number of requested items is greater than MaxLimit, a
        TooManyItems fault shall be returned.
        """
        return self.operator.call("GetCredentials", Token=Token)

    def GetCredentialList(self, Limit=None, StartReference=None):
        """This operation requests a list of all credential items provided by the
        device.

        A call to this method shall return a StartReference when not all data is
        returned and more data is available. The reference shall be valid for retrieving
        the next set of data. Please refer section 4.8.3 in [Access Control Service
        Specification] for more details. The number of items returned shall not be
        greater the Limit parameter.
        """
        return self.operator.call(
            "GetCredentialList", Limit=Limit, StartReference=StartReference
        )

    def CreateCredential(
        self, Credential, State
    ):  # pylint: disable=redefined-outer-name
        """This operation creates a credential.

        A call to this method takes a credential structure and a credential state
        structure as input parameters. The credential state can be created in disabled
        or enabled state. The token field of the credential shall be empty, the device
        shall allocate a token for the credential. The allocated token shall be returned
        in the response. If the client sends any value in the token field, the device
        shall return InvalidArgVal as generic fault code.
        """
        return self.operator.call(
            "CreateCredential", Credential=Credential, State=State
        )

    def SetCredential(self, CredentialData):
        """This method is used to synchronize a credential in a client with the
        device."""
        return self.operator.call("SetCredential", CredentialData=CredentialData)

    def ModifyCredential(self, Credential):  # pylint: disable=redefined-outer-name
        """This operation modifies the specified credential.

        The token of the credential to modify is specified in the token field of the
        Credential structure and shall not be empty. All other fields in the structure
        shall overwrite the fields in the specified credential. When an existing
        credential is modified, the state is not modified explicitly. The only way for a
        client to change the state of a credential is to explicitly call the
        EnableCredential, DisableCredential or ResetAntipassback command. All existing
        credential identifiers and credential access profiles are removed and replaced
        with the specified entities.
        """
        return self.operator.call("ModifyCredential", Credential=Credential)

    def DeleteCredential(self, Token):
        """This method deletes the specified credential.

        If it is associated with one or more entities some devices may not be able to
        delete the credential, and consequently a ReferenceInUse fault shall be
        generated.
        """
        return self.operator.call("DeleteCredential", Token=Token)

    def GetCredentialState(self, Token):
        """This method returns the state for the specified credential.

        If the capability ResetAntipassbackSupported is set to true, then the device
        shall supply the anti-passback state in the returned credential state structure.
        """
        return self.operator.call("GetCredentialState", Token=Token)

    def EnableCredential(self, Token, Reason=None):
        """This method is used to enable a credential."""
        return self.operator.call("EnableCredential", Token=Token, Reason=Reason)

    def DisableCredential(self, Token, Reason=None):
        """This method is used to disable a credential."""
        return self.operator.call("DisableCredential", Token=Token, Reason=Reason)

    def ResetAntipassbackViolation(self, CredentialToken):
        """This method is used to reset anti-passback violations for a specified
        credential."""
        return self.operator.call(
            "ResetAntipassbackViolation", CredentialToken=CredentialToken
        )

    def GetCredentialIdentifiers(self, CredentialToken):
        """This method returns all the credential identifiers for a credential."""
        return self.operator.call(
            "GetCredentialIdentifiers", CredentialToken=CredentialToken
        )

    def SetCredentialIdentifier(self, CredentialToken, CredentialIdentifier):
        """This operation creates or updates a credential identifier for a credential.

        If the type of specified credential identifier already exists, the current
        credential identifier of that type is replaced. Otherwise the credential
        identifier is added.
        """
        return self.operator.call(
            "SetCredentialIdentifier",
            CredentialToken=CredentialToken,
            CredentialIdentifier=CredentialIdentifier,
        )

    def DeleteCredentialIdentifier(self, CredentialToken, CredentialIdentifierTypeName):
        """This method deletes all the identifier values for the specified type.

        However, if the identifier type name doesn’t exist in the device, it will be
        silently ignored without any response.
        """
        return self.operator.call(
            "DeleteCredentialIdentifier",
            CredentialToken=CredentialToken,
            CredentialIdentifierTypeName=CredentialIdentifierTypeName,
        )

    def GetCredentialAccessProfiles(self, CredentialToken):
        """This method returns all the credential access profiles for a credential."""
        return self.operator.call(
            "GetCredentialAccessProfiles", CredentialToken=CredentialToken
        )

    def SetCredentialAccessProfiles(self, CredentialToken, CredentialAccessProfile):
        """This operation add or updates the credential access profiles for a
        credential.

        The device shall update the credential access profile if the access profile
        token in the specified credential access profile matches. Otherwise the
        credential access profile is added.
        """
        return self.operator.call(
            "SetCredentialAccessProfiles",
            CredentialToken=CredentialToken,
            CredentialAccessProfile=CredentialAccessProfile,
        )

    def DeleteCredentialAccessProfiles(self, CredentialToken, AccessProfileToken):
        """This method deletes all the credential access profiles for the specified
        tokens.

        However, if no matching credential access profiles are found, the corresponding
        access profile tokens are silently ignored without any response.
        """
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
        """This command requests a list of all whitelisted credential identifiers in the
        device.

        A device with capability MaxWhitelistedItems greater than zero, shall implement
        this command.
        """
        return self.operator.call(
            "GetWhitelist",
            Limit=Limit,
            StartReference=StartReference,
            IdentifierType=IdentifierType,
            FormatType=FormatType,
            Value=Value,
        )

    def AddToWhitelist(self, Identifier):
        """This command adds the specified credential identifiers to the whitelist.

        A device with capability MaxWhitelistedItems greater than zero, shall implement
        this command. If a specified whitelist item also is blacklisted, the item shall
        be removed from the blacklist.
        """
        return self.operator.call("AddToWhitelist", Identifier=Identifier)

    def RemoveFromWhitelist(self, Identifier):
        """This command removes the specified credential identifiers from the whitelist.

        A device with capability MaxWhitelistedItems greater than zero, shall implement
        this command. This command is idempotent and is safe to repeat even if the
        specified whitelist items do not exist.
        """
        return self.operator.call("RemoveFromWhitelist", Identifier=Identifier)

    def DeleteWhitelist(self):
        """This command deletes all credential identifiers from the whitelist.

        A device with capability MaxWhitelistedItems greater than zero, shall implement
        this command. This command is idempotent and is safe to repeat even if the
        whitelist already is empty.
        """
        return self.operator.call("DeleteWhitelist")

    def GetBlacklist(
        self,
        Limit=None,
        StartReference=None,
        IdentifierType=None,
        FormatType=None,
        Value=None,
    ):
        """This command requests a list of all blacklisted credential identifiers in the
        device.

        A device with capability MaxBlacklistedItems greater than zero, shall implement
        this command.
        """
        return self.operator.call(
            "GetBlacklist",
            Limit=Limit,
            StartReference=StartReference,
            IdentifierType=IdentifierType,
            FormatType=FormatType,
            Value=Value,
        )

    def AddToBlacklist(self, Identifier):
        """This command adds the specified credential identifiers to the blacklist.

        A device with capability MaxBlacklistedItems greater than zero, shall implement
        this command. If a specified blacklist item also is whitelisted, the item shall
        be removed from the whitelist.
        """
        return self.operator.call("AddToBlacklist", Identifier=Identifier)

    def RemoveFromBlacklist(self, Identifier):
        """This command removes the specified credential identifiers from the blacklist.

        A device with capability MaxBlacklistedItems greater than zero, shall implement
        this command. This command is idempotent and is safe to repeat even if the
        specified blacklist items do not exist.
        """
        return self.operator.call("RemoveFromBlacklist", Identifier=Identifier)

    def DeleteBlacklist(self):
        """This command deletes all credential identifiers from the blacklist.

        A device with capability MaxBlacklistedItems greater than zero, shall implement
        this command. This command is idempotent and is safe to repeat even if the
        blacklist already is empty.
        """
        return self.operator.call("DeleteBlacklist")
