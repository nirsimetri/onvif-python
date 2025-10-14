{
    'Analytics': {
        'XAddr': 'http://192.168.1.3/onvif/Analytics',
        'RuleSupport': False,
        'AnalyticsModuleSupport': False,
        '_value_1': None,
        '_attr_1': None
    },
    'Device': {
        'XAddr': 'http://192.168.1.3/onvif/device_service',
        'Network': {
            'IPFilter': False,
            'ZeroConfiguration': True,
            'IPVersion6': False,
            'DynDNS': False,
            'Extension': {
                '_value_1': [
                    <Element {http://www.onvif.org/ver10/schema}Dot11Configuration at 0x20766665700>,
                    <Element {http://www.onvif.org/ver10/schema}Extension at 0x20766665740>
                ],
                'Dot11Configuration': False,
                'Extension': {
                    'DHCPv6': False,
                    'Dot1XConfigurations': 0
                }
            },
            '_attr_1': None
        },
        'System': {
            'DiscoveryResolve': False,
            'DiscoveryBye': True,
            'RemoteDiscovery': True,
            'SystemBackup': False,
            'SystemLogging': False,
            'FirmwareUpgrade': True,
            'SupportedVersions': [
                {
                    'Major': 19,
                    'Minor': 12
                },
                {
                    'Major': 16,
                    'Minor': 12
                },
                {
                    'Major': 2,
                    'Minor': 60
                },
                {
                    'Major': 2,
                    'Minor': 40
                },
                {
                    'Major': 2,
                    'Minor': 20
                },
                {
                    'Major': 2,
                    'Minor': 10
                },
                {
                    'Major': 2,
                    'Minor': 0
                }
            ],
            'Extension': {
                '_value_1': [
                    <Element {http://www.onvif.org/ver10/schema}HttpFirmwareUpgrade at 0x20766667580>,
                    <Element {http://www.onvif.org/ver10/schema}HttpSystemBackup at 0x207666675c0>,
                    <Element {http://www.onvif.org/ver10/schema}HttpSystemLogging at 0x20766667600>,
                    <Element {http://www.onvif.org/ver10/schema}HttpSupportInformation at 0x20766667640>
                ],
                'HttpFirmwareUpgrade': True,
                'HttpSystemBackup': False,
                'HttpSystemLogging': False,
                'HttpSupportInformation': False,
                'Extension': None
            },
            '_attr_1': None
        },
        'IO': {
            'InputConnectors': 0,
            'RelayOutputs': 0,
            'Extension': {
                '_value_1': [
                    <Element {http://www.onvif.org/ver10/schema}Auxiliary at 0x2076666c1c0>,
                    <Element {http://www.onvif.org/ver10/schema}AuxiliaryCommands at 0x2076666c200>,
                    <Element {http://www.onvif.org/ver10/schema}Extension at 0x2076666c240>
                ],
                'Auxiliary': False,
                'AuxiliaryCommands': [],
                'Extension': None,
                '_attr_1': None
            },
            '_attr_1': None
        },
        'Security': {
            'TLS1.1': True,
            'TLS1.2': True,
            'OnboardKeyGeneration': False,
            'AccessPolicyConfig': False,
            'X.509Token': False,
            'SAMLToken': False,
            'KerberosToken': False,
            'RELToken': False,
            '_value_1': [
                <Element {http://www.onvif.org/ver10/schema}Extension at 0x2076666ce40>
            ],
            'Extension': {
                'TLS1.0': True,
                'Extension': {
                    'Dot1X': False,
                    'SupportedEAPMethod': 0,
                    'RemoteUserHandling': False
                }
            },
            '_attr_1': None
        },
        'Extension': None,
        '_attr_1': None
    },
    'Events': {
        'XAddr': 'http://192.168.1.3/onvif/Events',
        'WSSubscriptionPolicySupport': True,
        'WSPullPointSupport': True,
        'WSPausableSubscriptionManagerInterfaceSupport': False,
        '_value_1': None,
        '_attr_1': None
    },
    'Imaging': {
        'XAddr': 'http://192.168.1.3/onvif/Imaging',
        '_attr_1': None
    },
    'Media': {
        'XAddr': 'http://192.168.1.3/onvif/Media',
        'StreamingCapabilities': {
            'RTPMulticast': False,
            'RTP_TCP': True,
            'RTP_RTSP_TCP': True,
            'Extension': None,
            '_attr_1': None
        },
        '_value_1': [
            <Element {http://www.onvif.org/ver10/schema}Extension at 0x2076666e340>
        ],
        'Extension': {
            'ProfileCapabilities': {
                'MaximumNumberOfProfiles': 10
            }
        },
        '_attr_1': None
    },
    'PTZ': {
        'XAddr': 'http://192.168.1.3/onvif/PTZ',
        '_value_1': None,
        '_attr_1': None
    },
    'Extension': {
        '_value_1': [
            <Element {http://www.onvif.org/ver10/schema}DeviceIO at 0x20766664a40>,
            <Element {http://www.onvif.org/ver10/schema}Recording at 0x20766665280>,
            <Element {http://www.onvif.org/ver10/schema}Search at 0x20766665240>,
            <Element {http://www.onvif.org/ver10/schema}Replay at 0x20766665a00>
        ],
        'DeviceIO': {
            'XAddr': 'http://192.168.1.3/onvif/DeviceIO',
            'VideoSources': 1,
            'VideoOutputs': 0,
            'AudioSources': 1,
            'AudioOutputs': 1,
            'RelayOutputs': 0
        },
        'Display': None,
        'Recording': {
            'XAddr': 'http://192.168.1.3/onvif/Recording',
            'ReceiverSource': False,
            'MediaProfileSource': True,
            'DynamicRecordings': False,
            'DynamicTracks': False,
            'MaxStringLength': 64
        },
        'Search': {
            'XAddr': 'http://192.168.1.3/onvif/SearchRecording',
            'MetadataSearch': False
        },
        'Replay': {
            'XAddr': 'http://192.168.1.3/onvif/Replay'
        },
        'Receiver': None,
        'AnalyticsDevice': None,
        'Extensions': None
    },
    '_attr_1': None
}