"""Security (Dot1X) service implementation."""

from ...operator import ONVIFOperator
from ...utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class Dot1X(ONVIFService):
    """Security (Dot1X) service client.

    References:
        - First introduced: ONVIF Release 16.06 (June 2016)
        - Binding name: `Dot1XBinding` (ver10/advancedsecurity/wsdl/advancedsecurity.wsdl)
        - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/advancedsecurity/wsdl/advancedsecurity.wsdl
        - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/Security.xml
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("dot1x")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            xaddr=xaddr,
            **kwargs,
        )

    def AddDot1XConfiguration(self, Dot1XConfiguration):
        """This operation adds an IEEE 802.1X configuration to the device.

        Configurations are uniquely identified using IEEE 802.1X configuration IDs. The
        device shall ignore Dot1XID in the request, if present, and shall generate a
        unique configuration ID for the added configuration. If the command was
        successful, the device shall return the ID of the configuration. If the device
        does not have capacity for the configuration, the device shall produce a
        MaximumNumberOfDot1XConfigurationsReached fault and shall not add the
        configuration. If Identity is used as an anonymous identity for the
        corresponding authentication method, the device shall ignore an eventually
        supplied passphrase ID in the same Dot1XStage. Otherwise, if the device cannot
        process a passphrase ID included in the configuration to be added, the device
        shall produce a PassphraseID fault and shall not add the configuration. If the
        device cannot process a certification path ID included in the configuration to
        be added, the device shall produce a CertificationPathID fault and shall not add
        the configuration. If no certification path validation policy is stored under
        the requested certification path validation policy ID, the device shall produce
        a CertPathValidationPolicyID fault. If no certification path validation policy
        configured, authorization server certificate validation behavior is undefined
        and the device may either apply a vendor specific default validation policy or
        skip validation at all. If the device cannot process an authentication method
        included in the configuration to be added (e.g., unrecognized method or missing
        configuration parameter), the device shall produce a Dot1XMethod fault and shall
        not add the configuration. A device signalling support for IEEE 802.1X
        configuration with the MaximumNumberOfDot1XConfigurations capability shall
        support this command.
        """
        return self.operator.call(
            "AddDot1XConfiguration", Dot1XConfiguration=Dot1XConfiguration
        )

    def GetAllDot1XConfigurations(self):
        """This operation returns details of all IEEE 802.1X configurations that are on
        the device.

        This operation may be used, e.g., if a client lost track of which IEEE 802.1X
        configurations are present on the device. If no IEEE 802.1X configurations exist
        on the device, an empty list is returned. A device signalling support for IEEE
        802.1X configuration with the MaximumNumberOfDot1XConfigurations capability
        shall support this command.
        """
        return self.operator.call("GetAllDot1XConfigurations")

    def GetDot1XConfiguration(self, Dot1XID):
        """This operation returns details of a specific IEEE 802.1X configuration on the
        device.

        If the device cannot process the provided IEEE 802.1X configuration ID, the
        device shall produce a Dot1XConfigurationID fault. A device signalling support
        for IEEE 802.1X configuration with the MaximumNumberOfDot1XConfigurations
        capability shall support this command.
        """
        return self.operator.call("GetDot1XConfiguration", Dot1XID=Dot1XID)

    def DeleteDot1XConfiguration(self, Dot1XID):
        """This operation deletes an IEEE 802.1X configuration from the device.

        If the device cannot process the provided IEEE 802.1X configuration ID, the
        device shall produce a Dot1XConfigurationID fault. If a reference exists for the
        specified IEEE 802.1X configuration, the device shall produce a ReferenceExists
        fault and shall not delete the configuration. After an IEEE 802.1X configuration
        has been successfully deleted, the device may assign its former ID to a new
        configuration. A device signalling support for IEEE 802.1X configuration with
        the MaximumNumberOfDot1XConfigurations capability shall support this command.
        """
        return self.operator.call("DeleteDot1XConfiguration", Dot1XID=Dot1XID)

    def SetNetworkInterfaceDot1XConfiguration(self, token, Dot1XID):
        """This operation binds an IEEE 802.1X configuration to a network interface on
        the device.

        This operation shall either create a new binding or replace an existing binding.
        On failure when an existing binding already exists, the existing binding shall
        remain. The Device Management SetNetworkInterface operation provides a method of
        binding an IEEE 802.1X configuration to an IEEE 802.11 (wireless) interface, and
        that operation may still be used. But there is no ability for
        SetNetworkInterface to bind an IEEE 802.1X configuration to a hardwired
        interface. This operation is provided to bind an IEEE 802.1X configuration to
        either type of interface. If SetNetworkInterfaceDot1XConfiguration is used to
        bind an IEEE 802.1X configuration to an IEEE 802.11 (wireless) interface, then
        the DeviceManagement GetNetworkInterfaces operation shall return the IEEE 802.1X
        configuration ID along with the rest of that interface's configuration
        information. If the device cannot process the provided network interface token,
        the device shall produce an InvalidNetworkInterface fault. If the device cannot
        process the provided IEEE 802.1X configuration ID, the device shall produce a
        Dot1XConfigurationID fault. A device signalling support for IEEE 802.1X
        configuration with the MaximumNumberOfDot1XConfigurations capability shall
        support this command.
        """
        return self.operator.call(
            "SetNetworkInterfaceDot1XConfiguration", token=token, Dot1XID=Dot1XID
        )

    def GetNetworkInterfaceDot1XConfiguration(self, token):
        """This operation returns the IEEE 802.1X ID and configuration associated with a
        network interface on the device.

        If there is no IEEE 802.1X configuration associated with the specified network
        interface, then the response shall be empty. If the Device Management
        SetNetworkInterface operation was used to bind an IEEE 802.1X configuration to
        an IEEE 802.11 (wireless) interface, then this operation shall return the IEEE
        802.1X configuration information as if the SetNetworkInterfaceDot1XConfiguration
        operation had been used. If the device cannot process the provided network
        interface token, the device shall produce an InvalidNetworkInterface fault. A
        device signalling support for IEEE 802.1X configuration with the
        MaximumNumberOfDot1XConfigurations capability shall support this command.
        """
        return self.operator.call("GetNetworkInterfaceDot1XConfiguration", token=token)

    def DeleteNetworkInterfaceDot1XConfiguration(self, token):
        """This operation unbinds the IEEE 802.1X configuration associated with a
        network interface on the device.

        If there is no IEEE 802.1X configuration associated with the specified network
        interface, then the operation does nothing. The Device Management
        SetNetworkInterface operation provides a method of unbinding an IEEE 802.1X
        configuration from an IEEE 802.11 (wireless) interface by omitting the
        configuration ID, and that operation may still be used. But there is no ability
        for SetNetworkInterface to unbind an IEEE 802.1X configuration from a hardwired
        interface. This operation is provided to unbind an IEEE 802.1X configuration
        from either type of interface. If the Device Management SetNetworkInterface
        operation was used to bind an IEEE 802.1X configuration to an IEEE 802.11
        (wireless) interface, then this operation shall unbind the IEEE 802.1X
        configuration information as if the SetNetworkInterfaceDot1XConfiguration
        operation had been used. If the device cannot process the provided network
        interface token, the device shall produce an InvalidNetworkInterface fault. A
        device signalling support for IEEE 802.1X configuration with the
        MaximumNumberOfDot1XConfigurations capability shall support this command.
        """
        return self.operator.call(
            "DeleteNetworkInterfaceDot1XConfiguration", token=token
        )
