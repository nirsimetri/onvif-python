"""AuthenticationBehavior service implementation."""

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class AuthenticationBehavior(ONVIFService):
    """AuthenticationBehavior service client.

    References:
        - First introduced: ONVIF Release 18.06 (June 2018)
        - Binding name: `AuthenticationBehaviorBinding` (ver10/authenticationbehavior/wsdl/authenticationbehavior.wsdl)
        - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/authenticationbehavior/wsdl/authenticationbehavior.wsdl
        - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/AuthenticationBehavior.xml
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("authenticationbehavior")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="AuthenticationBehavior",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """This operation returns the capabilities of the authentication behavior
        service."""
        return self.operator.call("GetServiceCapabilities")

    def GetAuthenticationProfileInfo(self, Token):
        """This operation requests a list of AuthenticationProfileInfo items matching
        the given tokens.

        The device shall ignore tokens it cannot resolve and shall return an empty list
        if there are no items matching the specified tokens. The device shall not return
        a fault in this case.
        """
        return self.operator.call("GetAuthenticationProfileInfo", Token=Token)

    def GetAuthenticationProfileInfoList(self, Limit=None, StartReference=None):
        """This operation requests a list of all of AuthenticationProfileInfo items
        provided by the device.

        A call to this method shall return a StartReference when not all data is
        returned and more data is available. The reference shall be valid for retrieving
        the next set of data. Please refer Access Control Service Specification for more
        details. The number of items returned shall not be greater than Limit parameter.
        """
        return self.operator.call(
            "GetAuthenticationProfileInfoList",
            Limit=Limit,
            StartReference=StartReference,
        )

    def GetAuthenticationProfiles(self, Token):
        """This operation returns the specified AuthenticationProfile item matching the
        given tokens.

        The device shall ignore tokens it cannot resolve and shall return an empty list
        if there are no items matching specified tokens. The device shall not return a
        fault in this case.
        """
        return self.operator.call("GetAuthenticationProfiles", Token=Token)

    def GetAuthenticationProfileList(self, Limit=None, StartReference=None):
        """This operation requests a list of all of AuthenticationProfile items provided
        by the device.

        A call to this method shall return a StartReference when not all data is
        returned and more data is available. The reference shall be valid for retrieving
        the next set of data. Please refer Access Control Service Specification for more
        details. The number of items returned shall not be greater the Limit parameter.
        """
        return self.operator.call(
            "GetAuthenticationProfileList", Limit=Limit, StartReference=StartReference
        )

    def CreateAuthenticationProfile(self, AuthenticationProfile):
        """This operation creates the specified authentication profile in the device.

        The token field of the AuthenticationProfile structure shall be empty and the
        device shall allocate a token for the authentication profile. The allocated
        token shall be returned in the response. If the client sends any value in the
        token field, the device shall return InvalidArgVal as a generic fault code.
        """
        return self.operator.call(
            "CreateAuthenticationProfile", AuthenticationProfile=AuthenticationProfile
        )

    def SetAuthenticationProfile(self, AuthenticationProfile):
        """This method is used to synchronize an authentication profile in a client with
        the device.

        If an authentication profile with the specified token does not exist in the
        device, the authentication profile is created. If an authentication profile with
        the specified token exists, then the authentication profile is modified. A call
        to this method takes an AuthenticationProfile structure as input parameter. The
        token field of the AuthenticationProfile shall not be empty. A device that
        signals support for the ClientSuppliedTokenSupported capability shall implement
        this command.
        """
        return self.operator.call(
            "SetAuthenticationProfile", AuthenticationProfile=AuthenticationProfile
        )

    def ModifyAuthenticationProfile(self, AuthenticationProfile):
        """This operation modifies the specified authentication profile.

        The token of the authentication profile to modify is specified in the token
        field of the AuthenticationProfile structure and shall not be empty. All other
        fields in the structure shall overwrite the fields in the specified
        authentication profile.
        """
        return self.operator.call(
            "ModifyAuthenticationProfile", AuthenticationProfile=AuthenticationProfile
        )

    def DeleteAuthenticationProfile(self, Token):
        """This operation deletes the specified authentication profile.

        If the authentication profile is deleted, all authentication policies associated
        with the authentication profile will also be deleted. If it is associated with
        one or more entities some devices may not be able to delete the authentication
        profile, and consequently a ReferenceInUse fault shall be generated.
        """
        return self.operator.call("DeleteAuthenticationProfile", Token=Token)

    def GetSecurityLevelInfo(self, Token):
        """This operation requests a list of SecurityLevelInfo items matching the given
        tokens.

        The device shall ignore tokens it cannot resolve and shall return an empty list
        if there are no items matching the specified tokens. The device shall not return
        a fault in this case.
        """
        return self.operator.call("GetSecurityLevelInfo", Token=Token)

    def GetSecurityLevelInfoList(self, Limit=None, StartReference=None):
        """This operation requests a list of all of SecurityLevelInfo items provided by
        the device.

        A call to this method shall return a StartReference when not all data is
        returned and more data is available. The reference shall be valid for retrieving
        the next set of data. Please refer Access Control Service Specification for more
        details. The number of items returned shall not be greater than Limit parameter.
        """
        return self.operator.call(
            "GetSecurityLevelInfoList", Limit=Limit, StartReference=StartReference
        )

    def GetSecurityLevels(self, Token):
        """This operation returns the specified SecurityLevel item matching the given
        tokens.

        The device shall ignore tokens it cannot resolve and shall return an empty list
        if there are no items matching specified tokens. The device shall not return a
        fault in this case.
        """
        return self.operator.call("GetSecurityLevels", Token=Token)

    def GetSecurityLevelList(self, Limit=None, StartReference=None):
        """This operation requests a list of all of SecurityLevel items provided by the
        device.

        A call to this method shall return a StartReference when not all data is
        returned and more data is available. The reference shall be valid for retrieving
        the next set of data. Please refer Access Control Service Specification for more
        details. The number of items returned shall not be greater the Limit parameter.
        """
        return self.operator.call(
            "GetSecurityLevelList", Limit=Limit, StartReference=StartReference
        )

    def CreateSecurityLevel(self, SecurityLevel):
        """This operation creates the specified security level in the device.

        The token field of the SecurityLevel structure shall be empty and the device
        shall allocate a token for the security level. The allocated token shall be
        returned in the response. If the client sends any value in the token field, the
        device shall return InvalidArgVal as a generic fault code.
        """
        return self.operator.call("CreateSecurityLevel", SecurityLevel=SecurityLevel)

    def SetSecurityLevel(self, SecurityLevel):
        """This method is used to synchronize an security level in a client with the
        device.

        If an security level with the specified token does not exist in the device, the
        security level is created. If an security level with the specified token exists,
        then the security level is modified. A call to this method takes an
        SecurityLevel structure as input parameter. The token field of the SecurityLevel
        shall not be empty. A device that signals support for the
        ClientSuppliedTokenSupported capability shall implement this command.
        """
        return self.operator.call("SetSecurityLevel", SecurityLevel=SecurityLevel)

    def ModifySecurityLevel(self, SecurityLevel):
        """This operation modifies the specified security level.

        The token of the security level to modify is specified in the token field of the
        SecurityLevel structure and shall not be empty. All other fields in the
        structure shall overwrite the fields in the specified security level.
        """
        return self.operator.call("ModifySecurityLevel", SecurityLevel=SecurityLevel)

    def DeleteSecurityLevel(self, Token):
        """This operation deletes the specified security level.

        If the security level is deleted, all authentication policies associated with
        the security level will also be deleted. If it is associated with one or more
        entities some devices may not be able to delete the security level, and
        consequently a ReferenceInUse fault shall be generated.
        """
        return self.operator.call("DeleteSecurityLevel", Token=Token)
