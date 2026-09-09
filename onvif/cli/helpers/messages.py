"""CLI messages."""

from onvif.cli.utils import (
    colorize,
)
from onvif.meta import __repository__, __version__

INTERACTIVE_HELP = f"""
{colorize(f'ONVIF Interactive Shell — v{__version__}', 'cyan')}\n{colorize(__repository__, 'white')}

{colorize('Basic Commands:', 'yellow')}
  capabilities, caps       - Show device capabilities
  services                 - Show available services with details
  info                     - Show connection and device information
  exit                     - Exit the shell
  shortcuts                - Show available shortcuts

{colorize('Navigation Commands:', 'yellow')}
  <service>                - Enter service mode (e.g., devicemgmt, media)
  <service> <argument>     - Enter service mode with argument (e.g. pullpoint SubscriptionRef=<value>)
  cd <service>             - Enter service mode (alias)
  ls                       - List commands/services/methods in grid format
  up                       - Exit current service mode (go up one level)
  pwd                      - Show current service context
  clear                    - Clear terminal screen
  help <command>           - Show help for a specific command

{colorize('Service Mode Commands:', 'yellow')}
  desc <method>            - Show method documentation
  type <method>            - Show input/output types from WSDL

{colorize('Method Execution:', 'yellow')}
  <method>                 - Execute method without parameters
  <method> {{"param": "value"}}  - Execute method with JSON parameters
  <method> param=value     - Execute method with simple parameters

{colorize('Data Management:', 'yellow')}
  store <name>             - Store last result with a name
  show <name>              - Show stored data
  show <name>[0]           - Show element at index (for lists)
  show <name>.attribute    - Show specific attribute
  show                     - List all stored data
  rm <name>                - Remove stored data by name
  cls                      - Clear all stored data

{colorize('Using Stored Data in Methods:', 'yellow')}
  Use $variable syntax to reference stored data in method parameters:
  - $profiles[0].token                    - Access list element and attribute
  - $profiles[0].VideoSourceConfiguration.SourceToken

  Example:
    GetProfiles                           - Get profiles
    store profiles                        - Store result
    show profiles[0].token                - Show first profile token
    GetImagingSettings VideoSourceToken=$profiles[0].VideoSourceConfiguration.SourceToken

{colorize('Debug Commands:', 'yellow')}
  debug                    - Show last SOAP request & response (if --debug enabled)

{colorize('Tab Completion:', 'yellow')}
  Use {colorize('TAB', 'yellow')} key for auto-completion of commands, services, and methods
  Type partial commands to see suggestions

{colorize('Examples:', 'yellow')}
  192.168.1.17:8000 > caps                # Show capabilities
  192.168.1.17:8000 > dev<TAB>            # Completes to 'devicemgmt'
  192.168.1.17:8000 > cd devicemgmt       # Enter device management
  192.168.1.17:8000/devicemgmt > Get<TAB> # Show methods starting with 'Get'
  192.168.1.17:8000/devicemgmt > GetServices {{"IncludeCapability": true}}
  192.168.1.17:8000/devicemgmt > GetServices IncludeCapability=True
  192.168.1.17:8000/devicemgmt > store services_info
  192.168.1.17:8000/devicemgmt > up       # Exit service mode
  192.168.1.17:8000 >                     # Back to root context
            """

INTERACTIVE_SHORTCUTS = f"""
{colorize('Available Shortcuts:', 'cyan')}

{colorize('Navigation:', 'yellow')}
  <service>                - Enter service mode (e.g., devicemgmt, media)
  cd <service>             - Enter service (same as '<service>')
  ls                       - List commands/services in grid format (like TAB)
  up                       - Go up one level
  pwd                      - Show current context
  clear                    - Clear terminal screen
  help <command>           - Show help for a command

{colorize('Service Mode Commands:', 'yellow')}
  desc <method>            - Show method documentation
  type <method>            - Show input/output types from WSDL

{colorize('Quick Access:', 'yellow')}
  caps                     - Show capabilities (same as 'capabilities')

{colorize('Tab Completion Examples:', 'yellow')}
  dev<TAB>                 - Completes to 'devicemgmt'
  med<TAB>                 - Completes to 'media'
  Get<TAB>                 - Shows all methods starting with 'Get'
        """

# pylint: disable=line-too-long
CLI_EPILOG = f"""
Examples:
  # Product search
  {colorize('onvif', 'yellow')} --search c210
  {colorize('onvif', 'yellow')} -s "axis camera"
  {colorize('onvif', 'yellow')} --search hikvision --page 2 --per-page 5

  # Discover ONVIF devices on network
  {colorize('onvif', 'yellow')} --discover --username admin --password admin123 --interactive
  {colorize('onvif', 'yellow')} media GetProfiles --discover --username admin
  {colorize('onvif', 'yellow')} -d -i

  # Discover with filtering
  {colorize('onvif', 'yellow')} --discover --filter ptz --interactive
  {colorize('onvif', 'yellow')} -d -f "C210" -i
  {colorize('onvif', 'yellow')} -d -f "audio_encoder" -u admin -p admin123 -i

  # Direct command execution
  {colorize('onvif', 'yellow')} devicemgmt GetCapabilities Category=All --host 192.168.1.17 --port 8000 --username admin --password admin123
  {colorize('onvif', 'yellow')} ptz ContinuousMove ProfileToken=Profile_1 Velocity={{'PanTilt': {{'x': -0.1, 'y': 0}}}} -H 192.168.1.17 -P 8000 -u admin -p admin123

  # Save output to file
  {colorize('onvif', 'yellow')} devicemgmt GetDeviceInformation --host 192.168.1.17 --port 8000 --username admin --password admin123 --output device_info.json
  {colorize('onvif', 'yellow')} media GetProfiles --host 192.168.1.17 --port 8000 --username admin --password admin123 --output profiles.xml
  {colorize('onvif', 'yellow')} ptz GetConfigurations --host 192.168.1.17 --port 8000 --username admin --password admin123 --output ptz_config.txt --debug

  # Interactive mode
  {colorize('onvif', 'yellow')} --host 192.168.1.17 --port 8000 --username admin --password admin123 --interactive

  # Prompting for username and password
  # (if not provided)
  {colorize('onvif', 'yellow')} -H 192.168.1.17 -P 8000 -i

  # Using HTTPS
  {colorize('onvif', 'yellow')} media GetProfiles --host camera.example.com --port 443 --username admin --password admin123 --https
        """
