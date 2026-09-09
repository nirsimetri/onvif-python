"""AccessRules service implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class AccessRules(ONVIFService):
    """AccessRules service client.

    References:
    - First introduced: ONVIF Release 2.6 (June 2015)
    - Binding name: `AccessRulesBinding` (ver10/accessrules/wsdl/accessrules.wsdl)
    - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/accessrules/wsdl/accessrules.wsdl
    - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/AccessRules.xml
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("accessrules")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="AccessRules",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """This operation returns the capabilities of the access rules service."""
        return self.operator.call("GetServiceCapabilities")

    def GetAccessProfileInfo(self, Token):
        """This operation requests a list of AccessProfileInfo items matching the given
        tokens.

        The device shall ignore tokens it cannot resolve and shall return an empty list
        if there are no items matching the specified tokens. The device shall not return
        a fault in this case. If the number of requested items is greater than MaxLimit,
        a TooManyItems fault shall be returned.
        """
        return self.operator.call("GetAccessProfileInfo", Token=Token)

    def GetAccessProfileInfoList(self, Limit=None, StartReference=None):
        """This operation requests a list of all of AccessProfileInfo items provided by
        the device.

        A call to this method shall return a StartReference when not all data is
        returned and more data is available. The reference shall be valid for retrieving
        the next set of data. The number of items returned shall not be greater than the
        Limit parameter.
        """
        return self.operator.call(
            "GetAccessProfileInfoList", Limit=Limit, StartReference=StartReference
        )

    def GetAccessProfiles(self, Token):
        """This operation returns the specified access profile item matching the given
        tokens.

        The device shall ignore tokens it cannot resolve and shall return an empty list
        if there are no items matching specified tokens. The device shall not return a
        fault in this case. If the number of requested items is greater than MaxLimit, a
        TooManyItems fault shall be returned.
        """
        return self.operator.call("GetAccessProfiles", Token=Token)

    def GetAccessProfileList(self, Limit=None, StartReference=None):
        """This operation requests a list of all of access profile items provided by the
        device.

        A call to this method shall return a StartReference when not all data is
        returned and more data is available. The reference shall be valid for retrieving
        the next set of data. The number of items returned shall not be greater than the
        Limit parameter.
        """
        return self.operator.call(
            "GetAccessProfileList", Limit=Limit, StartReference=StartReference
        )

    def CreateAccessProfile(self, AccessProfile):
        """This operation creates the specified access profile in the device.

        The token field of the access profile shall be empty, the service shall allocate
        a token for the access profile. The allocated token shall be returned in the
        response. If the client sends any value in the token field, the device shall
        return InvalidArgVal as generic fault code. In an access profile, if several
        access policies specifying different schedules for the same access point will
        result in a union of the schedules.
        """
        return self.operator.call("CreateAccessProfile", AccessProfile=AccessProfile)

    def ModifyAccessProfile(self, AccessProfile):
        """This operation will modify the access profile for the specified access
        profile token.

        The token of the access profile to modify is specified in the token field of the
        AccessProile structure and shall not be empty. All other fields in the structure
        shall overwrite the fields in the specified access profile. If several access
        policies specifying different schedules for the same access point will result in
        a union of the schedules. If the device could not store the access profile
        information then a fault will be generated.
        """
        return self.operator.call("ModifyAccessProfile", AccessProfile=AccessProfile)

    def SetAccessProfile(self, AccessProfile):
        """This operation will synchronize an access profile in a client with the
        device.

        If an access profile with the specified token does not exist in the device, the
        access profile is created. If an access profile with the specified token exists,
        then the access profile is modified. A call to this method takes an access
        profile structure as input parameter. The token field of the access profile must
        not be empty. A device that signals support for the ClientSuppliedTokenSupported
        capability shall implement this command.
        """
        return self.operator.call("SetAccessProfile", AccessProfile=AccessProfile)

    def DeleteAccessProfile(self, Token):
        """This operation will delete the specified access profile.

        If the access profile is deleted, all access policies associated to the access
        profile will also be deleted. If it is associated with one or more entities some
        devices may not be able to delete the access profile, and consequently a
        ReferenceInUse fault shall be generated.
        """
        return self.operator.call("DeleteAccessProfile", Token=Token)
