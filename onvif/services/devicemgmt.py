"""Device (Core) service implementation."""

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name,too-many-public-methods
class Device(ONVIFService):
    """Device service client.

    References:
        - ONVIF Core
        - Binding name: `DeviceBinding` (ver10/device/wsdl/devicemgmt.wsdl)
        - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/device/wsdl/devicemgmt.wsdl
        - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/Core.xml
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("devicemgmt")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="device_service",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServices(self, IncludeCapability):
        """Returns information about services on the device."""
        return self.operator.call("GetServices", IncludeCapability=IncludeCapability)

    def GetServiceCapabilities(self):
        """Returns the capabilities of the device service.

        The result is returned in a typed answer.
        """
        return self.operator.call("GetServiceCapabilities")

    def GetDeviceInformation(self):
        """This operation gets basic device information from the device."""
        return self.operator.call("GetDeviceInformation")

    def SetSystemDateAndTime(
        self, DateTimeType, DaylightSavings, TimeZone=None, UTCDateTime=None
    ):
        """This operation sets the device system date and time.

        The device shall support the configuration of the daylight saving setting and of
        the manual system date and time (if applicable) or indication of NTP time (if
        applicable) through the SetSystemDateAndTime command.

        If system time and date are set manually, the client shall include UTCDateTime
        in the request.

        A TimeZone token which is not formed according to the rules of IEEE 1003.1
        section 8.3 is considered as invalid timezone.

        The DayLightSavings flag should be set to true to activate any DST settings of
        the TimeZone string. Clear the DayLightSavings flag if the DST portion of the
        TimeZone settings should be ignored.
        """
        return self.operator.call(
            "SetSystemDateAndTime",
            DateTimeType=DateTimeType,
            DaylightSavings=DaylightSavings,
            TimeZone=TimeZone,
            UTCDateTime=UTCDateTime,
        )

    def GetSystemDateAndTime(self):
        """This operation gets the device system date and time.

        The device shall support the return of the daylight saving setting and of the
        manual system date and time (if applicable) or indication of NTP time (if
        applicable) through the GetSystemDateAndTime command.

        A device shall provide the UTCDateTime information.
        """
        return self.operator.call("GetSystemDateAndTime")

    def SetSystemFactoryDefault(self, FactoryDefault):
        """This operation reloads the parameters on the device to their factory default
        values."""
        return self.operator.call(
            "SetSystemFactoryDefault", FactoryDefault=FactoryDefault
        )

    def UpgradeSystemFirmware(self, Firmware):
        """This operation upgrades a device firmware version.

        After a successful upgrade the response message is sent before the device
        reboots. The device should support firmware upgrade through the
        UpgradeSystemFirmware command. The exact format of the firmware data is outside
        the scope of this standard.
        """
        return self.operator.call("UpgradeSystemFirmware", Firmware=Firmware)

    def SystemReboot(self):
        """This operation reboots the device."""
        return self.operator.call("SystemReboot")

    def RestoreSystem(self, BackupFiles):
        """This operation restores the system backup configuration files(s) previously
        retrieved from a device.

        The device should support restore of backup configuration file(s) through the
        RestoreSystem command. The exact format of the backup configuration file(s) is
        outside the scope of this standard. If the command is supported, it shall accept
        backup files returned by the GetSystemBackup command.
        """
        return self.operator.call("RestoreSystem", BackupFiles=BackupFiles)

    def GetSystemBackup(self):
        """This operation is retrieves system backup configuration file(s) from a
        device.

        The device should support return of back up configuration file(s) through the
        GetSystemBackup command. The backup is returned with reference to a name and
        mime-type together with binary data. The exact format of the backup
        configuration files is outside the scope of this standard.
        """
        return self.operator.call("GetSystemBackup")

    def GetSystemLog(self, LogType):
        """This operation gets a system log from the device.

        The exact format of the system logs is outside the scope of this standard.
        """
        return self.operator.call("GetSystemLog", LogType=LogType)

    def GetSystemSupportInformation(self):
        """This operation gets arbitary device diagnostics information from the
        device."""
        return self.operator.call("GetSystemSupportInformation")

    def GetScopes(self):
        """This operation requests the scope parameters of a device.

        The scope parameters are used in the device discovery to match a probe message,
        see Section 7.

        The Scope parameters are of two different types:
        - Fixed
        - Configurable

        Fixed scope parameters are permanent device characteristics and
        cannot be removed through the device management interface. The scope type is
        indicated in the scope list returned in the get scope parameters response. A
        device shall support retrieval of discovery scope parameters through the
        GetScopes command. As some scope parameters are mandatory, the device shall
        return a non-empty scope list in the response.
        """
        return self.operator.call("GetScopes")

    def SetScopes(self, Scopes):
        """This operation sets the scope parameters of a device.

        The scope parameters are used in the device discovery to match a probe message.
        This operation replaces all existing configurable scope parameters (not fixed
        parameters). If this shall be avoided, one should use the scope add command
        instead. The device shall support configuration of discovery scope parameters
        through the SetScopes command.
        """
        return self.operator.call("SetScopes", Scopes=Scopes)

    def AddScopes(self, ScopeItem):
        """This operation adds new configurable scope parameters to a device.

        The scope parameters are used in the device discovery to match a probe message.
        The device shall support addition of discovery scope parameters through the
        AddScopes command.
        """
        return self.operator.call("AddScopes", ScopeItem=ScopeItem)

    def RemoveScopes(self, ScopeItem):
        """This operation deletes scope-configurable scope parameters from a device.

        The scope parameters are used in the device discovery to match a probe message,
        see Section 7. The device shall support deletion of discovery scope parameters
        through the RemoveScopes command. Table
        """
        return self.operator.call("RemoveScopes", ScopeItem=ScopeItem)

    def GetDiscoveryMode(self):
        """This operation gets the discovery mode of a device.

        See Section 7.2 for the definition of the different device discovery modes. The
        device shall support retrieval of the discovery mode setting through the
        GetDiscoveryMode command.
        """
        return self.operator.call("GetDiscoveryMode")

    def SetDiscoveryMode(self, DiscoveryMode):
        """This operation sets the discovery mode operation of a device.

        See Section 7.2 for the definition of the different device discovery modes. The
        device shall support configuration of the discovery mode setting through the
        SetDiscoveryMode command.
        """
        return self.operator.call("SetDiscoveryMode", DiscoveryMode=DiscoveryMode)

    def GetRemoteDiscoveryMode(self):
        """This operation gets the remote discovery mode of a device.

        See Section 7.4 for the definition of remote discovery extensions. A device that
        supports remote discovery shall support retrieval of the remote discovery mode
        setting through the GetRemoteDiscoveryMode command.
        """
        return self.operator.call("GetRemoteDiscoveryMode")

    def SetRemoteDiscoveryMode(self, RemoteDiscoveryMode):
        """This operation sets the remote discovery mode of operation of a device.

        See Section 7.4 for the definition of remote discovery remote extensions. A
        device that supports remote discovery shall support configuration of the
        discovery mode setting through the SetRemoteDiscoveryMode command.
        """
        return self.operator.call(
            "SetRemoteDiscoveryMode", RemoteDiscoveryMode=RemoteDiscoveryMode
        )

    def GetDPAddresses(self):
        """This operation gets the remote DP address or addresses from a device.

        If the device supports remote discovery, as specified in Section
        7.4, the device shall support retrieval of the remote DP
        address(es) through the GetDPAddresses command.
        """
        return self.operator.call("GetDPAddresses")

    def GetEndpointReference(self):
        """A client can ask for the device service endpoint reference address property
        that can be used to derive the password equivalent for remote user operation.

        The device shall support the GetEndpointReference command returning the address
        property of the device service endpoint reference.
        """
        return self.operator.call("GetEndpointReference")

    def GetRemoteUser(self):
        """This operation returns the configured remote user (if any).

        A device supporting remote user handling shall support this operation. The user
        is only valid for the WS-UserToken profile or as an HTTP / RTSP user.

        The algorithm to use for deriving the password is described in section 5.12.2.1
        of the core specification.
        """
        return self.operator.call("GetRemoteUser")

    def SetRemoteUser(self, RemoteUser=None):
        """This operation sets the remote user.

        A device supporting remote user handling shall support this
        operation. The user is only valid for the WS-UserToken profile
        or as an HTTP / RTSP user.

        The password that is set shall always be the original (not
        derived) password.

        If UseDerivedPassword is set password derivation shall be done
        by the device when connecting to a remote device.The algorithm
        to use for deriving the password is described in section
        5.12.2.1 of the core specification.

        To remove the remote user SetRemoteUser should be called without
        the RemoteUser parameter.
        """
        return self.operator.call("SetRemoteUser", RemoteUser=RemoteUser)

    def GetUserRoles(self, UserRole=None):
        """This operation returns the editable user levels configured in the device.

        Whenever an editable user level is passed in the request, information only about
        that level is returned.
        """
        return self.operator.call("GetUserRoles", UserRole=UserRole)

    def SetUserRole(self, UserRole):
        """This operation configures an editable user level in the device.

        If the level passed in UserRole already exists in the device, its configuration
        is overwritten. Otherwise, a new editable user level is created.
        """
        return self.operator.call("SetUserRole", UserRole=UserRole)

    def DeleteUserRole(self, UserRole):
        """This operation deletes an editable user level in the device."""
        return self.operator.call("DeleteUserRole", UserRole=UserRole)

    def GetUsers(self):
        """This operation lists the registered users and corresponding credentials on a
        device.

        The device shall support retrieval of registered device users and their
        credentials for the user token through the GetUsers command.
        """
        return self.operator.call("GetUsers")

    def CreateUsers(self, User):
        """This operation creates new device users and corresponding credentials on a
        device for authentication purposes.

        The device shall support creation of device users and their credentials through
        the CreateUsers command. Either all users are created successfully or a fault
        message shall be returned without creating any user.

        ONVIF compliant devices are recommended to support password length of at least
        28 bytes, as clients may follow the password derivation mechanism which results
        in 'password equivalent' of length 28 bytes, as described in section 3.1.2 of
        the ONVIF security white paper.
        """
        return self.operator.call("CreateUsers", User=User)

    def DeleteUsers(self, Username):
        """This operation deletes users on a device.

        The device shall support deletion of device users and their credentials through
        the DeleteUsers command. A device may have one or more fixed users that cannot
        be deleted to ensure access to the unit. Either all users are deleted
        successfully or a fault message shall be returned and no users be deleted.
        """
        return self.operator.call("DeleteUsers", Username=Username)

    def SetUser(self, User):
        """This operation updates the settings for one or several users on a device for
        authentication purposes.

        The device shall support update of device users and their credentials through
        the SetUser command. Either all change requests are processed successfully or a
        fault message shall be returned and no change requests be processed.
        """
        return self.operator.call("SetUser", User=User)

    def GetWsdlUrl(self):
        """This method allows to provide a URL where product specific WSDL and schema
        definitions can be retrieved.

        This method is deprecated.
        """
        return self.operator.call("GetWsdlUrl")

    def GetPasswordComplexityOptions(self):
        """This method allows retrieval of all the available parameters and their valid
        ranges for the password complexity configuration."""
        return self.operator.call("GetPasswordComplexityOptions")

    def GetPasswordComplexityConfiguration(self):
        """This method allows retrieval of the current password complexity configuration
        settings."""
        return self.operator.call("GetPasswordComplexityConfiguration")

    def SetPasswordComplexityConfiguration(
        self,
        MinLen=None,
        Uppercase=None,
        Number=None,
        SpecialChars=None,
        BlockUsernameOccurrence=None,
        PolicyConfigurationLocked=None,
    ):
        """This method allows setting of the password complexity configuration."""
        return self.operator.call(
            "SetPasswordComplexityConfiguration",
            MinLen=MinLen,
            Uppercase=Uppercase,
            Number=Number,
            SpecialChars=SpecialChars,
            BlockUsernameOccurrence=BlockUsernameOccurrence,
            PolicyConfigurationLocked=PolicyConfigurationLocked,
        )

    def GetPasswordHistoryConfiguration(self):
        """This method allows retrieval of the current password history configuration
        settings."""
        return self.operator.call("GetPasswordHistoryConfiguration")

    def SetPasswordHistoryConfiguration(self, Enabled, Length):
        """This method allows setting of the password history configuration."""
        return self.operator.call(
            "SetPasswordHistoryConfiguration", Enabled=Enabled, Length=Length
        )

    def GetAuthFailureWarningOptions(self):
        """This method allows retrieval of all the available parameters and their valid
        ranges for the authentication failure warning configuration."""
        return self.operator.call("GetAuthFailureWarningOptions")

    def GetAuthFailureWarningConfiguration(self):
        """This method allows retrieval of the current authentication failure warning
        configuration settings."""
        return self.operator.call("GetAuthFailureWarningConfiguration")

    def SetAuthFailureWarningConfiguration(
        self, Enabled, MonitorPeriod, MaxAuthFailures
    ):
        """This method allows setting of the authentication failure warning
        configuration."""
        return self.operator.call(
            "SetAuthFailureWarningConfiguration",
            Enabled=Enabled,
            MonitorPeriod=MonitorPeriod,
            MaxAuthFailures=MaxAuthFailures,
        )

    def GetCapabilities(self, Category=None):
        """This method has been replaced by the more generic GetServices method.

        For capabilities of individual services refer to the GetServiceCapabilities
        methods.
        """
        return self.operator.call("GetCapabilities", Category=Category)

    def SetDPAddresses(self, DPAddress=None):
        """This operation sets the remote DP address or addresses on a device.

        If the device supports remote discovery, as specified in Section
        7.4, the device shall support configuration of the remote DP
        address(es) through the SetDPAddresses command.
        """
        return self.operator.call("SetDPAddresses", DPAddress=DPAddress)

    def GetHostname(self):
        """This operation is used by an endpoint to get the hostname from a device.

        The device shall return its hostname configurations through the GetHostname
        command.
        """
        return self.operator.call("GetHostname")

    def SetHostname(self, Name):
        """This operation sets the hostname on a device.

        It shall be possible to set the device hostname configurations through the
        SetHostname command.

        A device shall accept string formated according to RFC 1123 section 2.1 or
        alternatively to RFC 952, other string shall be considered as invalid strings.
        """
        return self.operator.call("SetHostname", Name=Name)

    def SetHostnameFromDHCP(self, FromDHCP):
        """This operation controls whether the hostname is set manually or retrieved via
        DHCP."""
        return self.operator.call("SetHostnameFromDHCP", FromDHCP=FromDHCP)

    def GetDNS(self):
        """This operation gets the DNS settings from a device.

        The device shall return its DNS configurations through the GetDNS command.
        """
        return self.operator.call("GetDNS")

    def SetDNS(self, FromDHCP, SearchDomain=None, DNSManual=None):
        """This operation sets the DNS settings on a device.

        It shall be possible to set the device DNS configurations through the SetDNS
        command.
        """
        return self.operator.call(
            "SetDNS", FromDHCP=FromDHCP, SearchDomain=SearchDomain, DNSManual=DNSManual
        )

    def GetNTP(self):
        """This operation gets the NTP settings from a device.

        If the device supports NTP, it shall be possible to get the NTP server settings
        through the GetNTP command.
        """
        return self.operator.call("GetNTP")

    def SetNTP(self, FromDHCP, NTPManual=None):
        """This operation sets the NTP settings on a device.

        If the device supports NTP, it shall be possible to set the NTP server settings
        through the SetNTP command.

        A device shall accept string formated according to RFC 1123 section 2.1 or
        alternatively to RFC 952, other string shall be considered as invalid strings.

        Changes to the NTP server list will not affect the clock mode DateTimeType. Use
        SetSystemDateAndTime to activate NTP operation.
        """
        return self.operator.call("SetNTP", FromDHCP=FromDHCP, NTPManual=NTPManual)

    def GetDynamicDNS(self):
        """This operation gets the dynamic DNS settings from a device.

        If the device supports dynamic DNS as specified in [RFC 2136] and [RFC 4702], it
        shall be possible to get the type, name and TTL through the GetDynamicDNS
        command.
        """
        return self.operator.call("GetDynamicDNS")

    def SetDynamicDNS(self, Type, Name=None, TTL=None):
        """This operation sets the dynamic DNS settings on a device.

        If the device supports dynamic DNS as specified in [RFC 2136] and [RFC 4702], it
        shall be possible to set the type, name and TTL through the SetDynamicDNS
        command.
        """
        return self.operator.call("SetDynamicDNS", Type=Type, Name=Name, TTL=TTL)

    def GetNetworkInterfaces(self):
        """This operation gets the network interface configuration from a device.

        The device shall support return of network interface configuration settings as
        defined by the NetworkInterface type through the GetNetworkInterfaces command.
        """
        return self.operator.call("GetNetworkInterfaces")

    def SetNetworkInterfaces(self, InterfaceToken, NetworkInterface):
        """This operation sets the network interface configuration on a device.

        The device shall support network configuration of supported network interfaces
        through the SetNetworkInterfaces command.

        For interoperability with a client unaware of the IEEE 802.11 extension a device
        shall retain its IEEE 802.11 configuration if the IEEE 802.11 configuration
        element isn't present in the request.
        """
        return self.operator.call(
            "SetNetworkInterfaces",
            InterfaceToken=InterfaceToken,
            NetworkInterface=NetworkInterface,
        )

    def GetNetworkProtocols(self):
        """This operation gets defined network protocols from a device.

        The device shall support the GetNetworkProtocols command returning configured
        network protocols.
        """
        return self.operator.call("GetNetworkProtocols")

    def SetNetworkProtocols(self, NetworkProtocols):
        """This operation configures defined network protocols on a device.

        The device shall support configuration of defined network protocols through the
        SetNetworkProtocols command.
        """
        return self.operator.call(
            "SetNetworkProtocols", NetworkProtocols=NetworkProtocols
        )

    def GetNetworkDefaultGateway(self):
        """This operation gets the default gateway settings from a device.

        The device shall support the GetNetworkDefaultGateway command returning
        configured default gateway address(es).
        """
        return self.operator.call("GetNetworkDefaultGateway")

    def SetNetworkDefaultGateway(self, IPv4Address=None, IPv6Address=None):
        """This operation sets the default gateway settings on a device.

        The device shall support configuration of default gateway through the
        SetNetworkDefaultGateway command.
        """
        return self.operator.call(
            "SetNetworkDefaultGateway", IPv4Address=IPv4Address, IPv6Address=IPv6Address
        )

    def GetZeroConfiguration(self):
        """This operation gets the zero-configuration from a device.

        If the device supports dynamic IP configuration according to [RFC3927], it shall
        support the return of IPv4 zero configuration address and status through the
        GetZeroConfiguration command.

        Devices supporting zero configuration on more than one interface shall use the
        extension to list the additional interface settings.
        """
        return self.operator.call("GetZeroConfiguration")

    def SetZeroConfiguration(self, InterfaceToken, Enabled):
        """This operation sets the zero-configuration.

        Use GetCapabilities to get if zero-configuration is supported or not.
        """
        return self.operator.call(
            "SetZeroConfiguration", InterfaceToken=InterfaceToken, Enabled=Enabled
        )

    def GetIPAddressFilter(self):
        """This operation gets the IP address filter settings from a device.

        If the device supports device access control based on IP filtering rules (denied
        or accepted ranges of IP addresses), the device shall support the
        GetIPAddressFilter command.
        """
        return self.operator.call("GetIPAddressFilter")

    def SetIPAddressFilter(self, IPAddressFilter):
        """This operation sets the IP address filter settings on a device.

        If the device supports device access control based on IP filtering rules (denied
        or accepted ranges of IP addresses), the device shall support configuration of
        IP filtering rules through the SetIPAddressFilter command.
        """
        return self.operator.call("SetIPAddressFilter", IPAddressFilter=IPAddressFilter)

    def AddIPAddressFilter(self, IPAddressFilter):
        """This operation adds an IP filter address to a device.

        If the device supports device access control based on IP filtering rules (denied
        or accepted ranges of IP addresses), the device shall support adding of IP
        filtering addresses through the AddIPAddressFilter command.
        """
        return self.operator.call("AddIPAddressFilter", IPAddressFilter=IPAddressFilter)

    def RemoveIPAddressFilter(self, IPAddressFilter):
        """This operation deletes an IP filter address from a device.

        If the device supports device access control based on IP filtering rules (denied
        or accepted ranges of IP addresses), the device shall support deletion of IP
        filtering addresses through the RemoveIPAddressFilter command.
        """
        return self.operator.call(
            "RemoveIPAddressFilter", IPAddressFilter=IPAddressFilter
        )

    def GetAccessPolicy(self):
        """Access to different services and sub-sets of services should be subject to
        access control.

        The WS-Security framework gives the prerequisite for end-point authentication.
        Authorization decisions can then be taken using an access security policy. This
        standard does not mandate any particular policy description format or security
        policy but this is up to the device manufacturer or system provider to choose
        policy and policy description format of choice. However, an access policy (in
        arbitrary format) can be requested using this command. If the device supports
        access policy settings based on WS-Security authentication, then the device
        shall support this command.
        """
        return self.operator.call("GetAccessPolicy")

    def SetAccessPolicy(self, PolicyFile):
        """This command sets the device access security policy (for more details on the
        access security policy see the Get command).

        If the device supports access policy settings based on WS- Security
        authentication, then the device shall support this command.
        """
        return self.operator.call("SetAccessPolicy", PolicyFile=PolicyFile)

    def CreateCertificate(
        self, CertificateID=None, Subject=None, ValidNotBefore=None, ValidNotAfter=None
    ):
        """This operation creates a new certificate on the device."""
        return self.operator.call(
            "CreateCertificate",
            CertificateID=CertificateID,
            Subject=Subject,
            ValidNotBefore=ValidNotBefore,
            ValidNotAfter=ValidNotAfter,
        )

    def GetCertificates(self):
        """This operation gets the list of certificates on the device."""
        return self.operator.call("GetCertificates")

    def GetCertificatesStatus(self):
        """This operation gets the status of the certificates on the device."""
        return self.operator.call("GetCertificatesStatus")

    def SetCertificatesStatus(self, CertificateStatus=None):
        """This operation sets the status of the certificates on the device."""
        return self.operator.call(
            "SetCertificatesStatus", CertificateStatus=CertificateStatus
        )

    def DeleteCertificates(self, CertificateID):
        """This operation deletes a certificate on the device."""
        return self.operator.call("DeleteCertificates", CertificateID=CertificateID)

    def GetPkcs10Request(self, CertificateID, Subject=None, Attributes=None):
        """This operation gets the PKCS#10 request for a certificate on the device."""
        return self.operator.call(
            "GetPkcs10Request",
            CertificateID=CertificateID,
            Subject=Subject,
            Attributes=Attributes,
        )

    def LoadCertificates(self, NVTCertificate):
        """This operation loads certificates onto the device."""
        return self.operator.call("LoadCertificates", NVTCertificate=NVTCertificate)

    def GetClientCertificateMode(self):
        """This operation gets the client certificate mode."""
        return self.operator.call("GetClientCertificateMode")

    def SetClientCertificateMode(self, Enabled):
        """This operation sets the client certificate mode."""
        return self.operator.call("SetClientCertificateMode", Enabled=Enabled)

    def GetCACertificates(self):
        """This operation gets the list of CA certificates on the device."""
        return self.operator.call("GetCACertificates")

    def LoadCertificateWithPrivateKey(self, CertificateWithPrivateKey):
        """This operation loads a certificate with private key onto the device."""
        return self.operator.call(
            "LoadCertificateWithPrivateKey",
            CertificateWithPrivateKey=CertificateWithPrivateKey,
        )

    def GetCertificateInformation(self, CertificateID):
        """This operation gets the information of a specific certificate."""
        return self.operator.call(
            "GetCertificateInformation", CertificateID=CertificateID
        )

    def LoadCACertificates(self, CACertificate):
        """This operation loads CA certificates onto the device."""
        return self.operator.call("LoadCACertificates", CACertificate=CACertificate)

    def GetRelayOutputs(self):
        """This operation gets a list of all available relay outputs and their settings.

        This method has been deprecated with version 2.0. Refer to the DeviceIO service.
        """
        return self.operator.call("GetRelayOutputs")

    def SetRelayOutputSettings(self, RelayOutputToken, Properties):
        """This operation sets the settings of a relay output.

        This method has been deprecated with version 2.0. Refer to the DeviceIO service.
        """
        return self.operator.call(
            "SetRelayOutputSettings",
            RelayOutputToken=RelayOutputToken,
            Properties=Properties,
        )

    def SetRelayOutputState(self, RelayOutputToken, LogicalState):
        """This operation sets the state of a relay output.

        This method has been deprecated with version 2.0. Refer to the DeviceIO service.
        """
        return self.operator.call(
            "SetRelayOutputState",
            RelayOutputToken=RelayOutputToken,
            LogicalState=LogicalState,
        )

    def SendAuxiliaryCommand(self, AuxiliaryCommand):
        """Manage auxiliary commands supported by a device, such as controlling an
        Infrared (IR) lamp, a heater or a wiper or a thermometer that is connected to
        the device.

        The supported commands can be retrieved via the AuxiliaryCommands capability.

        Although the name of the auxiliary commands can be freely defined, commands
        starting with the prefix tt: are reserved to define frequently used commands and
        these reserved commands shall all share the "tt:command|parameter" syntax.

        - tt:Wiper|On - Request to start the wiper.
        - tt:Wiper|Off - Request to stop the wiper.
        - tt:Washer|On - Request to start the washer.
        - tt:Washer|Off - Request to stop the washer.
        - tt:WashingProcedure|On - Request to start the washing procedure.
        - tt: WashingProcedure |Off - Request to stop the washing procedure.
        - tt:IRLamp|On - Request to turn ON an IR illuminator attached to the unit.
        - tt:IRLamp|Off - Request to turn OFF an IR illuminator attached to the unit.
        - tt:IRLamp|Auto - Request to configure an IR illuminator attached to the unit so that it automatically turns ON and OFF.

        A device that indicates auxiliary service capability shall support this command.
        """
        return self.operator.call(
            "SendAuxiliaryCommand", AuxiliaryCommand=AuxiliaryCommand
        )

    def CreateDot1XConfiguration(self, Dot1XConfiguration):
        """This operation creates a new 802.1X configuration on the device."""
        return self.operator.call(
            "CreateDot1XConfiguration", Dot1XConfiguration=Dot1XConfiguration
        )

    def SetDot1XConfiguration(self, Dot1XConfiguration):
        """This operation sets the 802.1X configuration on the device."""
        return self.operator.call(
            "SetDot1XConfiguration", Dot1XConfiguration=Dot1XConfiguration
        )

    def GetDot1XConfiguration(self, Dot1XConfigurationToken):
        """This operation gets the 802.1X configuration from the device."""
        return self.operator.call(
            "GetDot1XConfiguration", Dot1XConfigurationToken=Dot1XConfigurationToken
        )

    def GetDot1XConfigurations(self):
        """This operation gets the list of 802.1X configurations from the device."""
        return self.operator.call("GetDot1XConfigurations")

    def DeleteDot1XConfiguration(self, Dot1XConfigurationToken=None):
        """This operation deletes an 802.1X configuration from the device."""
        return self.operator.call(
            "DeleteDot1XConfiguration", Dot1XConfigurationToken=Dot1XConfigurationToken
        )

    def GetDot11Capabilities(self):
        """This operation returns the IEEE802.11 capabilities.

        The device shall support this operation.
        """
        return self.operator.call("GetDot11Capabilities")

    def GetDot11Status(self, InterfaceToken):
        """This operation returns the status of a wireless network interface.

        The device shall support this command.
        """
        return self.operator.call("GetDot11Status", InterfaceToken=InterfaceToken)

    def ScanAvailableDot11Networks(self, InterfaceToken):
        """This operation returns a lists of the wireless networks in range of the
        device.

        A device should support this operation.
        """
        return self.operator.call(
            "ScanAvailableDot11Networks", InterfaceToken=InterfaceToken
        )

    def GetSystemUris(self):
        """This operation is used to retrieve URIs from which system information may be
        downloaded using HTTP.

        URIs may be returned for the following system information:

        System Logs. Multiple system logs may be returned, of different types.
        The exact format of the system logs is outside the scope of this specification.

        Support Information. This consists of arbitrary device diagnostics information from a device.
        The exact format of the diagnostic information is outside the scope of this specification.

        System Backup. The received file is a backup file that can be used to restore the current
        device configuration at a later date. The exact format of the backup configuration file
        is outside the scope of this specification.

        If the device allows retrieval of system logs, support information or system backup data,
        it should make them available via HTTP GET. If it does, it shall support the GetSystemUris command.
        """
        return self.operator.call("GetSystemUris")

    def StartFirmwareUpgrade(self):
        """This operation initiates a firmware upgrade using the HTTP POST mechanism.

        The response to the command includes an HTTP URL to which the upgrade file may
        be uploaded. The actual upgrade takes place as soon as the HTTP POST operation
        has completed. The device should support firmware upgrade through the
        StartFirmwareUpgrade command. The exact format of the firmware data is outside
        the scope of this specification. Firmware upgrade over HTTP may be achieved
        using the following steps:

        1. Client calls StartFirmwareUpgrade.
        2. Server responds with upload URI and optional delay value.
        3. Client waits for delay duration if specified by server.
        4. Client transmits the firmware image to the upload URI using HTTP POST.
        5. Server reprograms itself using the uploaded image, then reboots.

        If the firmware upgrade fails because the upgrade file was invalid, the HTTP
        POST response shall be "415 Unsupported Media Type". If the firmware upgrade
        fails due to an error at the device, the HTTP POST response shall be "500
        Internal Server Error".

        The value of the Content-Type header in the HTTP POST request shall be
        "application/octetstream".
        """
        return self.operator.call("StartFirmwareUpgrade")

    def UpgradeFirmware(self, Version):
        """This operation initiates a firmware upgrade using between the device and the
        MCS, without further actions from the client.

        Cloud firmware upgrade may be achieved using the following steps:
        1. Client retrieves the list of available firmware versions from the MCS.
        2. Client calls UpgradeFirmware, selecting the desired FW version.
        3. Device service responds with a downtime value.
        4. Device and MCS perform the firmware upgrade procedure without further interaction from the Client.
        5. Device notifies the Client of the result by emitting the appropriate CloudFirmwareUpgrade event

        After applying a firmware upgrade the device shall keep the basic network
        configuration like IP address, subnet mask and gateway or DHCP settings, as well
        as all the parameters of the Uplink and Security service unchanged, so that it
        can connect to the cloud. Additionally a firmware upgrade shall not change user
        credentials.
        """
        return self.operator.call("UpgradeFirmware", Version=Version)

    def StartSystemRestore(self):
        """This operation initiates a system restore from backed up configuration data
        using the HTTP POST mechanism.

        The response to the command includes an HTTP URL to which the backup file may be
        uploaded. The actual restore takes place as soon as the HTTP POST operation has
        completed. Devices should support system restore through the StartSystemRestore
        command. The exact format of the backup configuration data is outside the scope
        of this specification.

        System restore over HTTP may be achieved using the following steps:
        1. Client calls StartSystemRestore.
        2. Server responds with upload URI.
        3. Client transmits the configuration data to the upload URI using HTTP POST.
        4. Server applies the uploaded configuration, then reboots if necessary.

        If the system restore fails because the uploaded file was invalid, the HTTP POST
        response shall be "415 Unsupported Media Type". If the system restore fails due
        to an error at the device, the HTTP POST response shall be "500 Internal Server
        Error".

        The value of the Content-Type header in the HTTP POST request shall be
        "application/octetstream".
        """
        return self.operator.call("StartSystemRestore")

    def GetStorageConfigurations(self):
        """This operation lists all existing storage configurations for the device."""
        return self.operator.call("GetStorageConfigurations")

    def CreateStorageConfiguration(self, StorageConfiguration):
        """This operation creates a new storage configuration.

        The configuration data shall be created in the device and shall be persistent
        (remain after reboot).
        """
        return self.operator.call(
            "CreateStorageConfiguration", StorageConfiguration=StorageConfiguration
        )

    def GetStorageConfiguration(self, Token):
        """This operation retrieves the Storage configuration associated with the given
        storage configuration token."""
        return self.operator.call("GetStorageConfiguration", Token=Token)

    def SetStorageConfiguration(self, StorageConfiguration):
        """This operation modifies an existing Storage configuration."""
        return self.operator.call(
            "SetStorageConfiguration", StorageConfiguration=StorageConfiguration
        )

    def DeleteStorageConfiguration(self, Token):
        """This operation deletes the given storage configuration and configuration
        change shall always be persistent."""
        return self.operator.call("DeleteStorageConfiguration", Token=Token)

    def GetGeoLocation(self):
        """This operation lists all existing geo location configurations for the
        device."""
        return self.operator.call("GetGeoLocation")

    def SetGeoLocation(self, Location):
        """This operation allows to modify one or more geo configuration entries."""
        return self.operator.call("SetGeoLocation", Location=Location)

    def DeleteGeoLocation(self, Location):
        """This operation deletes the given geo location entries."""
        return self.operator.call("DeleteGeoLocation", Location=Location)

    def SetHashingAlgorithm(self, Algorithm):
        """This operation sets the hashing algorithm(s) used in HTTP and RTSP Digest
        Authentication."""
        return self.operator.call("SetHashingAlgorithm", Algorithm=Algorithm)
