"""PTZ service implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name,too-many-public-methods
class PTZ(ONVIFService):
    """PTZ service client.

    | Property | Details |
    | --- | --- |
    | **First introduced** | ONVIF Release 2.1 (June 2011) Split from Core 2.0 |
    | **Binding name** | `PTZBinding` (`ver20/ptz/wsdl/ptz.wsdl`) |
    | **Operations** | [ptz.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/ptz/wsdl/ptz.wsdl) |
    | **Specification** | [PTZ.xml](https://developer.onvif.org/pub/specs/branches/development/doc/PTZ.xml) |
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("ptz", "ver20")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="PTZ",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """Returns the capabilities of the PTZ service.

        The result is returned in a typed answer.
        """
        return self.operator.call("GetServiceCapabilities")

    def GetConfigurations(self):
        """Get all the existing PTZConfigurations from the device.

        The default Position/Translation/Velocity Spaces are introduced to allow NVCs
        sending move requests without the need to specify a certain coordinate system.

        The default Speeds are introduced to control the speed of move requests
        (absolute, relative, preset), where no explicit speed has been set.

        The allowed pan and tilt range for Pan/Tilt Limits is defined by a two-
        dimensional space range that is mapped to a specific Absolute Pan/Tilt Position
        Space. At least one Pan/Tilt Position Space is required by the PTZNode to
        support Pan/Tilt limits. The limits apply to all supported absolute, relative
        and continuous Pan/Tilt movements. The limits shall be checked within the
        coordinate system for which the limits have been specified. That means that even
        if movements are specified in a different coordinate system, the requested
        movements shall be transformed to the coordinate system of the limits where the
        limits can be checked. When a relative or continuous movements is specified,
        which would leave the specified limits, the PTZ unit has to move along the
        specified limits. The Zoom Limits have to be interpreted accordingly.
        """
        return self.operator.call("GetConfigurations")

    def GetPresets(self, ProfileToken):
        """Operation to request all PTZ presets for the PTZNode in the selected profile.

        The operation is supported if there is support for at least on PTZ preset by the
        PTZNode.
        """
        return self.operator.call("GetPresets", ProfileToken=ProfileToken)

    def SetPreset(self, ProfileToken, PresetName=None, PresetToken=None):
        """The SetPreset command saves the current device position parameters so that
        the device can move to the saved preset position through the GotoPreset
        operation.

        In order to create a new preset, the SetPresetRequest contains no PresetToken.
        If creation is successful, the Response contains the PresetToken which uniquely
        identifies the Preset. An existing Preset can be overwritten by specifying the
        PresetToken of the corresponding Preset. In both cases (overwriting or creation)
        an optional PresetName can be specified. The operation fails if the PTZ device
        is moving during the SetPreset operation. The device MAY internally save
        additional states such as imaging properties in the PTZ Preset which then should
        be recalled in the GotoPreset operation.
        """
        return self.operator.call(
            "SetPreset",
            ProfileToken=ProfileToken,
            PresetName=PresetName,
            PresetToken=PresetToken,
        )

    def RemovePreset(self, ProfileToken, PresetToken):
        """Operation to remove a PTZ preset for the Node in the selected profile.

        The operation is supported if the PresetPosition capability exists for teh Node
        in the selected profile.
        """
        return self.operator.call(
            "RemovePreset", ProfileToken=ProfileToken, PresetToken=PresetToken
        )

    def GotoPreset(self, ProfileToken, PresetToken, Speed=None):
        """Operation to go to a saved preset position for the PTZNode in the selected
        profile.

        The operation is supported if there is support for at least on PTZ preset by the
        PTZNode.
        """
        return self.operator.call(
            "GotoPreset",
            ProfileToken=ProfileToken,
            PresetToken=PresetToken,
            Speed=Speed,
        )

    def GetStatus(self, ProfileToken):
        """Operation to request PTZ status for the Node in the selected profile."""
        return self.operator.call("GetStatus", ProfileToken=ProfileToken)

    def GetConfiguration(self, PTZConfigurationToken):
        """Get a specific PTZconfiguration from the device, identified by its reference
        token or name.

        The default Position/Translation/Velocity Spaces are introduced to allow NVCs
        sending move requests without the need to specify a certain coordinate system.

        The default Speeds are introduced to control the speed of move requests
        (absolute, relative, preset), where no explicit speed has been set.

        The allowed pan and tilt range for Pan/Tilt Limits is defined by a two-
        dimensional space range that is mapped to a specific Absolute Pan/Tilt Position
        Space. At least one Pan/Tilt Position Space is required by the PTZNode to
        support Pan/Tilt limits. The limits apply to all supported absolute, relative
        and continuous Pan/Tilt movements. The limits shall be checked within the
        coordinate system for which the limits have been specified. That means that even
        if movements are specified in a different coordinate system, the requested
        movements shall be transformed to the coordinate system of the limits where the
        limits can be checked. When a relative or continuous movements is specified,
        which would leave the specified limits, the PTZ unit has to move along the
        specified limits. The Zoom Limits have to be interpreted accordingly.
        """
        return self.operator.call(
            "GetConfiguration", PTZConfigurationToken=PTZConfigurationToken
        )

    def GetNodes(self):
        """Get the descriptions of the available PTZ Nodes.

        A PTZ-capable device may have multiple PTZ Nodes. The PTZ Nodes may represent
        mechanical PTZ drivers, uploaded PTZ drivers or digital PTZ drivers. PTZ Nodes
        are the lowest level entities in the PTZ control API and reflect the supported
        PTZ capabilities. The PTZ Node is referenced either by its name or by its
        reference token.
        """
        return self.operator.call("GetNodes")

    def GetNode(self, NodeToken):
        """Get a specific PTZ Node identified by a reference token or a name."""
        return self.operator.call("GetNode", NodeToken=NodeToken)

    def SetConfiguration(self, PTZConfiguration, ForcePersistence):
        """Set/update a existing PTZConfiguration on the device."""
        return self.operator.call(
            "SetConfiguration",
            PTZConfiguration=PTZConfiguration,
            ForcePersistence=ForcePersistence,
        )

    def GetConfigurationOptions(self, ConfigurationToken):
        """List supported coordinate systems including their range limitations.

        Therefore, the options MAY differ depending on whether the PTZ Configuration is
        assigned to a Profile containing a Video Source Configuration. In that case, the
        options may additionally contain coordinate systems referring to the image
        coordinate system described by the Video Source Configuration. If the PTZ Node
        supports continuous movements, it shall return a Timeout Range within which
        Timeouts are accepted by the PTZ Node.
        """
        return self.operator.call(
            "GetConfigurationOptions", ConfigurationToken=ConfigurationToken
        )

    def GotoHomePosition(self, ProfileToken, Speed=None):
        """Operation to move the PTZ device to it's "home" position.

        The operation is supported if the HomeSupported element in the PTZNode is true.
        """
        return self.operator.call(
            "GotoHomePosition", ProfileToken=ProfileToken, Speed=Speed
        )

    def SetHomePosition(self, ProfileToken):
        """Operation to save current position as the home position.

        The SetHomePosition command returns with a failure if the "home" position is
        fixed and cannot be overwritten. If the SetHomePosition is successful, it is
        possible to recall the Home Position with the GotoHomePosition command.
        """
        return self.operator.call("SetHomePosition", ProfileToken=ProfileToken)

    def ContinuousMove(self, ProfileToken, Velocity, Timeout=None):
        """Operation for continuous Pan/Tilt and Zoom movements.

        The operation is supported if the PTZNode supports at least one continuous
        Pan/Tilt or Zoom space. If the space argument is omitted, the default space set
        by the PTZConfiguration will be used.
        """
        return self.operator.call(
            "ContinuousMove",
            ProfileToken=ProfileToken,
            Velocity=Velocity,
            Timeout=Timeout,
        )

    def RelativeMove(self, ProfileToken, Translation, Speed=None):
        """Operation for Relative Pan/Tilt and Zoom Move.

        The operation is supported if the PTZNode supports at least one relative
        Pan/Tilt or Zoom space.

        The speed argument is optional. If an x/y speed value is given it is up to the
        device to either use the x value as absolute resoluting speed vector or to map x
        and y to the component speed. If the speed argument is omitted, the default
        speed set by the PTZConfiguration will be used.
        """
        return self.operator.call(
            "RelativeMove",
            ProfileToken=ProfileToken,
            Translation=Translation,
            Speed=Speed,
        )

    def AbsoluteMove(self, ProfileToken, Position, Speed=None):
        """Operation to move pan,tilt or zoom to a absolute destination.

        The speed argument is optional. If an x/y speed value is given it is up to the
        device to either use the x value as absolute resoluting speed vector or to map x
        and y to the component speed. If the speed argument is omitted, the default
        speed set by the PTZConfiguration will be used.
        """
        return self.operator.call(
            "AbsoluteMove", ProfileToken=ProfileToken, Position=Position, Speed=Speed
        )

    def GeoMove(
        self, ProfileToken, Target, Speed=None, AreaHeight=None, AreaWidth=None
    ):
        """Operation to move pan,tilt or zoom to point to a destination based on the
        geolocation of the target.

        The speed argument is optional. If an x/y speed value is given it is up to the
        device to either use the x value as absolute resoluting speed vector or to map x
        and y to the component speed. If the speed argument is omitted, the default
        speed set by the PTZConfiguration will be used. The area height and area dwidth
        parameters are optional, they can be used independently and may be used by the
        device to automatically determine the best zoom level to show the target.
        """
        return self.operator.call(
            "GeoMove",
            ProfileToken=ProfileToken,
            Target=Target,
            Speed=Speed,
            AreaHeight=AreaHeight,
            AreaWidth=AreaWidth,
        )

    def Stop(self, ProfileToken, PanTilt=None, Zoom=None):
        """Operation to stop ongoing pan, tilt and zoom movements of absolute relative
        and continuous type.

        If no stop argument for pan, tilt or zoom is set, the device will stop all
        ongoing pan, tilt and zoom movements.
        """
        return self.operator.call(
            "Stop", ProfileToken=ProfileToken, PanTilt=PanTilt, Zoom=Zoom
        )

    def SendAuxiliaryCommand(self, ProfileToken, AuxiliaryData):
        """Operation to send auxiliary commands to the PTZ device mapped by the PTZNode
        in the selected profile.

        The operation is supported if the AuxiliarySupported element of the PTZNode is
        true
        """
        return self.operator.call(
            "SendAuxiliaryCommand",
            ProfileToken=ProfileToken,
            AuxiliaryData=AuxiliaryData,
        )

    def GetPresetTours(self, ProfileToken):
        """Operation to request PTZ preset tours in the selected media profiles."""
        return self.operator.call("GetPresetTours", ProfileToken=ProfileToken)

    def GetPresetTour(self, ProfileToken, PresetTourToken):
        """Operation to request a specific PTZ preset tour in the selected media
        profile."""
        return self.operator.call(
            "GetPresetTour", ProfileToken=ProfileToken, PresetTourToken=PresetTourToken
        )

    def GetPresetTourOptions(self, ProfileToken, PresetTourToken=None):
        """Operation to request available options to configure PTZ preset tour."""
        return self.operator.call(
            "GetPresetTourOptions",
            ProfileToken=ProfileToken,
            PresetTourToken=PresetTourToken,
        )

    def CreatePresetTour(self, ProfileToken):
        """Operation to create a preset tour for the selected media profile."""
        return self.operator.call("CreatePresetTour", ProfileToken=ProfileToken)

    def ModifyPresetTour(self, ProfileToken, PresetTour):
        """Operation to modify a preset tour for the selected media profile."""
        return self.operator.call(
            "ModifyPresetTour", ProfileToken=ProfileToken, PresetTour=PresetTour
        )

    def OperatePresetTour(self, ProfileToken, PresetTourToken, Operation):
        """Operation to perform specific operation on the preset tour in selected media
        profile."""
        return self.operator.call(
            "OperatePresetTour",
            ProfileToken=ProfileToken,
            PresetTourToken=PresetTourToken,
            Operation=Operation,
        )

    def RemovePresetTour(self, ProfileToken, PresetTourToken):
        """Operation to delete a specific preset tour from the media profile."""
        return self.operator.call(
            "RemovePresetTour",
            ProfileToken=ProfileToken,
            PresetTourToken=PresetTourToken,
        )

    def GetCompatibleConfigurations(self, ProfileToken):
        """Operation to get all available PTZConfigurations that can be added to the
        referenced media profile.

        A device providing more than one PTZConfiguration or more than one
        VideoSourceConfiguration or which has any other resource interdependency between
        PTZConfiguration entities and other resources listable in a media profile should
        implement this operation. PTZConfiguration entities returned by this operation
        shall not fail on adding them to the referenced media profile.
        """
        return self.operator.call(
            "GetCompatibleConfigurations", ProfileToken=ProfileToken
        )

    def MoveAndStartTracking(
        self,
        ProfileToken,
        ObjectID,
        PresetToken=None,
        GeoLocation=None,
        TargetPosition=None,
        Speed=None,
    ):
        """Operation to send an an atomic command to the device: move the camera to a
        wanted position and then delegate the PTZ control to the tracking algorithm.

        An existing Speed argument overrides DefaultSpeed of the corresponding PTZ
        configuration during movement to the requested position. If spaces are
        referenced within the Speed argument, they shall be speed spaces supported by
        the PTZ node.

        If the detection and the tracking are done in the same device, an ObjectID
        reference can be passed as an argument, in order to specify which object should
        be tracked.

        The operation shall fail if the requested absolute position is not reachable.
        """
        return self.operator.call(
            "MoveAndStartTracking",
            ProfileToken=ProfileToken,
            PresetToken=PresetToken,
            GeoLocation=GeoLocation,
            TargetPosition=TargetPosition,
            Speed=Speed,
            ObjectID=ObjectID,
        )
