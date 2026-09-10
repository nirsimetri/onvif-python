"""AppManagement service implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class AppManagement(ONVIFService):
    """AppManagement service client.

    | Property | Details |
    | --- | --- |
    | **First introduced** | ONVIF Release 19.12 (December 2019) |
    | **Binding name** | `AppManagementBinding` (`ver10/appmgmt/wsdl/appmgmt.wsdl`) |
    | **Operations** | [appmgmt.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/appmgmt/wsdl/appmgmt.wsdl) |
    | **Specification** | [AppMgmt.xml](https://developer.onvif.org/pub/specs/branches/development/doc/AppMgmt.xml) |
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("appmgmt")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="AppManagement",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """Returns the capabilities of the app management service."""
        return self.operator.call("GetServiceCapabilities")

    def Uninstall(self, AppID):
        """Removes an app from a device.

        This method shall return immedeiately and not wait until the application is
        completely removed. On completion or failure the method shall generate an
        UninstallCompletion event.
        """
        return self.operator.call("Uninstall", AppID=AppID)

    def GetInstalledApps(self):
        """List installed apps on the device."""
        return self.operator.call("GetInstalledApps")

    def GetAppsInfo(self, AppID=None):
        """The caller may provide an application ID to retrieve the information for a
        single application.

        If no application ID is provided the device shall report the information for all
        installed applications.
        """
        return self.operator.call("GetAppsInfo", AppID=AppID)

    def Activate(self, AppID):
        """Starts an application."""
        return self.operator.call("Activate", AppID=AppID)

    def Deactivate(self, AppID):
        """Stops an application."""
        return self.operator.call("Deactivate", AppID=AppID)

    def InstallLicense(self, License, AppID=None):
        """Installs a license to the device.

        If the device requires PerApp licensing than the AppID parameter shall be
        provided.
        """
        return self.operator.call("InstallLicense", AppID=AppID, License=License)

    def GetDeviceId(self):
        """Get the unique device id to which the licenses are issued."""
        return self.operator.call("GetDeviceId")
