"""AccessControl service implementation."""

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name,too-many-public-methods
class AccessControl(ONVIFService):
    """AccessControl service client.

    References:
        - First introduced: ONVIF Release 2.3 (May 2013)
        - Binding name: `PACSBinding` (ver10/pacs/accesscontrol.wsdl)
        - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/pacs/accesscontrol.wsdl
        - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/AccessControl.xml
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("accesscontrol")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="AccessControl",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """This operation returns the capabilities of the access control service.

        A device which provides the access control service shall implement this method.
        """
        return self.operator.call("GetServiceCapabilities")

    def GetAccessPointInfoList(self, Limit=None, StartReference=None):
        """This operation requests a list of all AccessPointInfo items provided by the
        device.

        A call to this method shall return a StartReference when not all data is
        returned and more data is available. The reference shall be valid for retrieving
        the next set of data. Please refer to section 4.8.3 in [ONVIF PACS Architecture
        and Design Considerations] for more details. The number of items returned shall
        not be greater than the Limit parameter.
        """
        return self.operator.call(
            "GetAccessPointInfoList", Limit=Limit, StartReference=StartReference
        )

    def GetAccessPointInfo(self, Token):
        """This operation requests a list of AccessPointInfo items matching the given
        tokens.

        The device shall ignore tokens it cannot resolve and shall return an empty list
        if there are no items matching the specified tokens. The device shall not return
        a fault in this case. If the number of requested items is greater than MaxLimit,
        a TooManyItems fault shall be returned.
        """
        return self.operator.call("GetAccessPointInfo", Token=Token)

    def GetAccessPointList(self, Limit=None, StartReference=None):
        """This operation requests a list of all AccessPoint items provided by the
        device.

        A call to this method shall return a StartReference when not all data is
        returned and more data is available. The reference shall be valid for retrieving
        the next set of data. The number of items returned shall not be greater than the
        Limit parameter.
        """
        return self.operator.call(
            "GetAccessPointList", Limit=Limit, StartReference=StartReference
        )

    def GetAccessPoints(self, Token):
        """This operation requests a list of AccessPoint items matching the given
        tokens.

        The device shall ignore tokens it cannot resolve and shall return an empty list
        if there are no items matching the specified tokens. The device shall not return
        a fault in this case. If the number of requested items is greater than MaxLimit,
        a TooManyItems fault shall be returned.
        """
        return self.operator.call("GetAccessPoints", Token=Token)

    def CreateAccessPoint(self, AccessPoint):
        """This operation creates the specified access point in the device.

        The token field of the AccessPoint structure shall be empty and the device shall
        allocate a token for the access point. The allocated token shall be returned in
        the response. If the client sends any value in the token field, the device shall
        return InvalidArgVal as a generic fault code.
        """
        return self.operator.call("CreateAccessPoint", AccessPoint=AccessPoint)

    def SetAccessPoint(self, AccessPoint):
        """This method is used to synchronize an access point in a client with the
        device.

        If an access point with the specified token does not exist in the device, the
        access point is created. If an access point with the specified token exists,
        then the access point is modified. A call to this method takes an AccessPoint
        structure as input parameter. The token field of the AccessPoint structure shall
        not be empty. A device that signals support for the ClientSuppliedTokenSupported
        capability shall implement this command. If no token was specified in the
        request, the device shall return InvalidArgs as a generic fault code.
        """
        return self.operator.call("SetAccessPoint", AccessPoint=AccessPoint)

    def ModifyAccessPoint(self, AccessPoint):
        """This operation modifies the specified access point.

        The token of the access point to modify is specified in the token field of the
        AccessPoint structure and shall not be empty. All other fields in the structure
        shall overwrite the fields in the specified access point. If no token was
        specified in the request, the device shall return InvalidArgs as a generic fault
        code.
        """
        return self.operator.call("ModifyAccessPoint", AccessPoint=AccessPoint)

    def DeleteAccessPoint(self, Token):
        """This operation deletes the specified access point.

        If it is associated with one or more entities some devices may not be able to
        delete the access point, and consequently a ReferenceInUse fault shall be
        generated. If no token was specified in the request, the device shall return
        InvalidArgs as a generic fault code.
        """
        return self.operator.call("DeleteAccessPoint", Token=Token)

    def SetAccessPointAuthenticationProfile(self, Token, AuthenticationProfileToken):
        """This operation defines the authentication behavior for an access point."""
        return self.operator.call(
            "SetAccessPointAuthenticationProfile",
            Token=Token,
            AuthenticationProfileToken=AuthenticationProfileToken,
        )

    def DeleteAccessPointAuthenticationProfile(self, Token):
        """This operation reverts the authentication behavior for an access point to its
        default behavior."""
        return self.operator.call("DeleteAccessPointAuthenticationProfile", Token=Token)

    def GetAreaInfoList(self, Limit=None, StartReference=None):
        """This operation requests a list of all AreaInfo items provided by the device.

        A call to this method shall return a StartReference when not all data is
        returned and more data is available. The reference shall be valid for retrieving
        the next set of data. The number of items returned shall not be greater than the
        Limit parameter.
        """
        return self.operator.call(
            "GetAreaInfoList", Limit=Limit, StartReference=StartReference
        )

    def GetAreaInfo(self, Token):
        """This operation requests a list of AreaInfo items matching the given tokens.

        The device shall ignore tokens it cannot resolve and shall return an empty list
        if there are no items matching the specified tokens. The device shall not return
        a fault in this case. If the number of requested items is greater than MaxLimit,
        a TooManyItems fault shall be returned.
        """
        return self.operator.call("GetAreaInfo", Token=Token)

    def GetAreaList(self, Limit=None, StartReference=None):
        """This operation requests a list of all Area items provided by the device.

        A call to this method shall return a StartReference when not all data is
        returned and more data is available. The reference shall be valid for retrieving
        the next set of data. The number of items returned shall not be greater than the
        Limit parameter.
        """
        return self.operator.call(
            "GetAreaList", Limit=Limit, StartReference=StartReference
        )

    def GetAreas(self, Token):
        """This operation requests a list of Area items matching the given tokens.

        The device shall ignore tokens it cannot resolve and shall return an empty list
        if there are no items matching the specified tokens. The device shall not return
        a fault in this case. If the number of requested items is greater than MaxLimit,
        a TooManyItems fault shall be returned.
        """
        return self.operator.call("GetAreas", Token=Token)

    def CreateArea(self, Area):
        """This operation creates the specified area in the device.

        The token field of the Area structure shall be empty and the device shall
        allocate a token for the area. The allocated token shall be returned in the
        response. If the client sends any value in the token field, the device shall
        return InvalidArgVal as a generic fault code.
        """
        return self.operator.call("CreateArea", Area=Area)

    def SetArea(self, Area):
        """This method is used to synchronize an area in a client with the device.

        If an area with the specified token does not exist in the device, the area is
        created. If an area with the specified token exists, then the area is modified.
        A call to this method takes an Area structure as input parameter. The token
        field of the Area structure shall not be empty. A device that signals support
        for the ClientSuppliedTokenSupported capability shall implement this command. If
        no token was specified in the request, the device shall return InvalidArgs as a
        generic fault code.
        """
        return self.operator.call("SetArea", Area=Area)

    def ModifyArea(self, Area):
        """This operation modifies the specified area.

        The token of the area to modify is specified in the token field of the Area
        structure and shall not be empty. All other fields in the structure shall
        overwrite the fields in the specified area. If no token was specified in the
        request, the device shall return InvalidArgs as a generic fault code.
        """
        return self.operator.call("ModifyArea", Area=Area)

    def DeleteArea(self, Token):
        """This operation deletes the specified area.

        If it is associated with one or more entities some devices may not be able to
        delete the area, and consequently a ReferenceInUse fault shall be generated. If
        no token was specified in the request, the device shall return InvalidArgs as a
        generic fault code.
        """
        return self.operator.call("DeleteArea", Token=Token)

    def GetAccessPointState(self, Token):
        """This operation requests the AccessPointState for the access point instance
        specified by the token."""
        return self.operator.call("GetAccessPointState", Token=Token)

    def EnableAccessPoint(self, Token):
        """This operation allows enabling an access point.

        A device that signals support for DisableAccessPoint capability for a particular
        access point instance shall implement this command.
        """
        return self.operator.call("EnableAccessPoint", Token=Token)

    def DisableAccessPoint(self, Token):
        """This operation allows disabling an access point.

        A device that signals support for the DisableAccessPoint capability for a
        particular access point instance shall implement this command.
        """
        return self.operator.call("DisableAccessPoint", Token=Token)

    def Feedback(
        self, AccessPointToken, FeedbackType, RecognitionType=None, TextMessage=None
    ):
        """This operation controls how the specified access point should indicate
        feedback.

        A client can instruct the access point about the door status or that one or more
        identifiers are needed to grant access, etc. It is typically used in conjunction
        with the AccessControl/Request/Identifier event and the ExternalAuthorization
        operation to indicate progress and required recognition methods. The supported
        feedback types are indicated in the SupportedFeedbackTypes field in the access
        point capabilities. In cases where multiple combinations of recognition methods
        are possible, the RecognitionType field can contain multiple values. E.g. for
        the security level "Card+PIN or Card+Fingerprint", the feedback command for
        requesting the second recognition method would contain both pt:PIN and
        pt:Fingerprint in the RecognitionType field. If the device supports at least one
        feedback type the device shall implement this command.
        """
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
        """This operation allows to deny or grant decision at an access point instance.

        A device that signals support for ExternalAuthorization capability for a
        particular access point instance shall implement this method.
        """
        return self.operator.call(
            "ExternalAuthorization",
            AccessPointToken=AccessPointToken,
            CredentialToken=CredentialToken,
            Reason=Reason,
            Decision=Decision,
        )
