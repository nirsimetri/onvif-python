"""
Path: examples/device_discovery.py
Author: @kaburagisec
Created: October 18, 2025

This script uses WS-Discovery protocol to discover all ONVIF-compliant devices
on the local network. It sends a custom SOAP Probe message via UDP multicast
and parses the ProbeMatches responses.

Requirements:
    No external dependencies required (uses standard library only)

Note:
    - The discovery process uses UDP multicast to 239.255.255.250:3702
    - Each probe must have a unique urn:uuid for devices to respond
    - Timeout is set to 4 seconds to collect all responses
    - Ensure your firewall allows UDP multicast traffic
"""

import socket
import uuid
import xml.etree.ElementTree as ET
import sys
import struct


# WS-Discovery constants
WS_DISCOVERY_TIMEOUT = 4  # 4 seconds - time to wait to receive packets
WS_DISCOVERY_PORT = 3702
WS_DISCOVERY_ADDRESS_IPv4 = "239.255.255.250"

# WS-Discovery Probe message template
# Note: Each probe MUST have a unique urn:uuid or devices will NOT reply!
WS_DISCOVERY_PROBE_MESSAGE = """<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:tds="http://www.onvif.org/ver10/device/wsdl" xmlns:tns="http://schemas.xmlsoap.org/ws/2005/04/discovery" xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing">
   <soap:Header>
      <wsa:Action>http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</wsa:Action>
      <wsa:MessageID>urn:uuid:{uuid}</wsa:MessageID>
      <wsa:To>urn:schemas-xmlsoap-org:ws:2005:04:discovery</wsa:To>
   </soap:Header>
   <soap:Body>
      <tns:Probe>
         <tns:Types>tds:Device</tns:Types>
      </tns:Probe>
   </soap:Body>
</soap:Envelope>"""


def get_network_interface():
    """Get the local network interface IP address."""
    try:
        # Create a socket to determine the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Warning: Error getting local network interface: {e}")
        return "0.0.0.0"


def send_probe_and_get_responses(network_interface=None, timeout=WS_DISCOVERY_TIMEOUT):
    """
    Compose and send a WS-Discovery Probe to discover ONVIF devices on the network.

    This function sends a SOAP Probe message via UDP multicast and collects all
    ProbeMatches responses from ONVIF devices.

    Args:
        network_interface (str): Network interface IP to bind to (None for auto-detect)
        timeout (int): Timeout in seconds to wait for responses

    Returns:
        list: Collection of all SOAP-infused XML ProbeMatch responses
    """
    # Generate unique urn:uuid for this probe
    probe_uuid = str(uuid.uuid4())

    # Create the probe message with unique UUID
    probe = WS_DISCOVERY_PROBE_MESSAGE.format(uuid=probe_uuid)

    # Determine network interface
    if network_interface is None:
        network_interface = get_network_interface()

    print(f"Network interface: {network_interface}")
    print(f"Probe UUID: {probe_uuid}")
    print(f"Sending Probe to: {WS_DISCOVERY_ADDRESS_IPv4}:{WS_DISCOVERY_PORT}")
    print("-" * 55)

    responses = []

    try:
        # Create UDP socket for sending and receiving
        sender_and_receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sender_and_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind to specific interface and port
        sender_and_receiver.bind((network_interface, 0))

        # Set socket timeout
        sender_and_receiver.settimeout(timeout)

        # Set TTL for multicast
        ttl = struct.pack("b", 1)
        sender_and_receiver.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

        # Send the probe message
        multicast_address = (WS_DISCOVERY_ADDRESS_IPv4, WS_DISCOVERY_PORT)
        sender_and_receiver.sendto(probe.encode("utf-8"), multicast_address)

        print(f"Probe sent! Waiting for responses (timeout: {timeout}s)...\n")

        # Receive responses
        receiver_buffer_size = 8192

        while True:
            try:
                data, addr = sender_and_receiver.recvfrom(receiver_buffer_size)
                response = data.decode("utf-8", errors="ignore")

                # Quick validation: check if response looks like valid XML
                response_stripped = response.strip()
                if response_stripped and len(response_stripped) > 10:
                    if response_stripped.startswith(
                        "<?xml"
                    ) or response_stripped.startswith("<"):
                        # Looks like valid XML, add to responses
                        responses.append(
                            {"xml": response, "address": addr[0], "port": addr[1]}
                        )
                        print(f"Received ProbeMatch ← {addr[0]}:{addr[1]}")
                    # else: silently ignore non-XML responses
                # else: silently ignore empty/too short responses

            except socket.timeout:
                # Timeout means no more responses
                print("\nSocket timeout - no more responses")
                break
            except Exception as e:
                print(f"Error receiving packet: {e}")
                break

        # Close socket
        sender_and_receiver.close()

    except Exception as e:
        print(f"Error during discovery: {e}")
        import traceback

        traceback.print_exc()

    return responses


def parse_probe_match(xml_response):
    """Parse SOAP ProbeMatch XML response to extract device information."""
    try:
        # Clean up the XML response (remove null bytes and whitespace)
        xml_response = xml_response.strip()

        # Skip empty or invalid responses
        if not xml_response or len(xml_response) < 10:
            return None

        # Check if it looks like XML
        if not xml_response.startswith("<?xml") and not xml_response.startswith("<"):
            return None

        # Define XML namespaces
        namespaces = {
            "soap": "http://www.w3.org/2003/05/soap-envelope",
            "wsa": "http://schemas.xmlsoap.org/ws/2004/08/addressing",
            "wsd": "http://schemas.xmlsoap.org/ws/2005/04/discovery",
            "d": "http://schemas.xmlsoap.org/ws/2005/04/discovery",
            "tds": "http://www.onvif.org/ver10/device/wsdl",
        }

        # Parse XML
        root = ET.fromstring(xml_response)

        # Find ProbeMatch element
        probe_match = root.find(".//d:ProbeMatch", namespaces)
        if probe_match is None:
            probe_match = root.find(".//wsd:ProbeMatch", namespaces)

        if probe_match is None:
            # Not a ProbeMatch response, skip it
            return None

        device_info = {
            "epr": "",
            "types": [],
            "scopes": [],
            "xaddrs": [],
            "metadata_version": "",
        }

        # Extract EndpointReference
        epr = probe_match.find(".//wsa:EndpointReference/wsa:Address", namespaces)
        if epr is not None:
            device_info["epr"] = epr.text

        # Extract Types
        types_elem = probe_match.find(".//d:Types", namespaces)
        if types_elem is None:
            types_elem = probe_match.find(".//wsd:Types", namespaces)
        if types_elem is not None and types_elem.text:
            device_info["types"] = types_elem.text.split()

        # Extract Scopes
        scopes_elem = probe_match.find(".//d:Scopes", namespaces)
        if scopes_elem is None:
            scopes_elem = probe_match.find(".//wsd:Scopes", namespaces)
        if scopes_elem is not None and scopes_elem.text:
            device_info["scopes"] = scopes_elem.text.split()

        # Extract XAddrs
        xaddrs_elem = probe_match.find(".//d:XAddrs", namespaces)
        if xaddrs_elem is None:
            xaddrs_elem = probe_match.find(".//wsd:XAddrs", namespaces)
        if xaddrs_elem is not None and xaddrs_elem.text:
            device_info["xaddrs"] = xaddrs_elem.text.split()

        # Extract MetadataVersion
        metadata_elem = probe_match.find(".//d:MetadataVersion", namespaces)
        if metadata_elem is None:
            metadata_elem = probe_match.find(".//wsd:MetadataVersion", namespaces)
        if metadata_elem is not None and metadata_elem.text:
            device_info["metadata_version"] = metadata_elem.text

        return device_info

    except ET.ParseError as e:
        # XML parsing error - not a valid XML, skip silently
        return None
    except Exception as e:
        # Other errors - log but don't crash
        print(f"Warning: Error parsing response: {e}")
        return None


def discover_onvif_devices(network_interface=None, timeout=WS_DISCOVERY_TIMEOUT):
    """Discover ONVIF devices on the network using WS-Discovery."""
    # Send probe and collect responses
    responses = send_probe_and_get_responses(network_interface, timeout)

    print(f"\n{'-'*55}")
    print(f"Total responses received: {len(responses)}")

    discovered_devices = []

    for idx, response in enumerate(responses, 1):
        # Parse the XML response
        device_info = parse_probe_match(response["xml"])

        # Only add valid ONVIF devices (ignore invalid/empty responses)
        if device_info:
            device_info["index"] = len(discovered_devices) + 1
            device_info["response_from"] = response["address"]
            discovered_devices.append(device_info)

    print(f"Valid ONVIF devices found: {len(discovered_devices)}")
    print(f"{'-'*55}\n")

    # Print device information
    for device in discovered_devices:
        print_device_info(device)

    return discovered_devices


def print_device_info(device, is_onvif=True):
    """Print formatted device information from ProbeMatch response."""
    print(f"[#{device['index']}] - {device.get('response_from', 'Unknown')}")
    print("EndpointReference (EPR):")
    print(f"  • {device['epr']}")

    if device["types"]:
        print("Types (from ProbeMatch):")
        for type_info in device["types"]:
            print(f"  • {type_info}")

    if device["xaddrs"]:
        print("Service Addresses (XAddrs):")
        for xaddr in device["xaddrs"]:
            print(f"  • {xaddr}")
            # Extract and display IP address and port
            if "://" in xaddr:
                try:
                    protocol = xaddr.split("://")[0]
                    rest = xaddr.split("://")[1]
                    ip_part = rest.split(":")[0].split("/")[0]

                    if ":" in rest.split("/")[0]:
                        port_part = rest.split(":")[1].split("/")[0]
                        print(
                            f"    → IP: {ip_part}, Port: {port_part}, Protocol: {protocol}"
                        )
                    else:
                        default_port = "80" if protocol == "http" else "443"
                        print(
                            f"    → IP: {ip_part}, Port: {default_port}, Protocol: {protocol}"
                        )
                except Exception as e:
                    print(f"Warning: Error parsing xaddrs: {e}")
                    pass

    if device["scopes"]:
        print("Scopes (ONVIF Metadata):")
        for scope in device["scopes"]:
            # Remove the prefix "onvif://www.onvif.org/" if present
            if scope.startswith("onvif://www.onvif.org/"):
                simplified = scope.replace("onvif://www.onvif.org/", "")
                print(f"  • [{simplified}]")
            else:
                # Keep other scopes as-is
                print(f"  • [{scope}]")

    if device.get("metadata_version"):
        print(f"Metadata Version: {device['metadata_version']}")

    print()


if __name__ == "__main__":
    try:
        discover_onvif_devices(network_interface=None, timeout=WS_DISCOVERY_TIMEOUT)
    except KeyboardInterrupt:
        print("\n\nDiscovery interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
