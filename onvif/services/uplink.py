"""Uplink service implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class Uplink(ONVIFService):
    """Uplink service client.

    | Property | Details |
    | --- | --- |
    | **First introduced** | ONVIF Release 18.12 (December 2018) |
    | **Binding name** | `UplinkBinding` (`ver10/uplink/wsdl/uplink.wsdl`) |
    | **Operations** | [uplink.wsdl)]([uplink.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/uplink/wsdl/uplink.wsdl)) |
    | **Specification** | [Uplink.xml)]([Uplink.xml](https://developer.onvif.org/pub/specs/branches/development/doc/Uplink.xml)) |
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("uplink")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Uplink",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """Returns the capabilities of the uplink service."""
        return self.operator.call("GetServiceCapabilities")

    def GetUplinks(self):
        """A device supporting uplinks shall support this command to retrieve the
        configured uplink configurations.

        The Status field shall signal whether a connection is Offline, Connecting or
        Online.
        """
        return self.operator.call("GetUplinks")

    def SetUplink(self, Configuration):
        """A device supporting uplinks shall support this command to add or modify an
        uplink configuration.

        The Status property of the UplinkConfiguration shall be ignored by the device. A
        device shall use the field RemoteAddress to decide whether to update an existing
        entry or create a new entry.
        """
        return self.operator.call("SetUplink", Configuration=Configuration)

    def DeleteUplink(self, RemoteAddress):
        """A device supporting uplinks shall support this command to remove an uplink
        configuration."""
        return self.operator.call("DeleteUplink", RemoteAddress=RemoteAddress)
