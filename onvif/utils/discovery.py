# onvif/utils/discovery.py

import socket
import uuid
import xml.etree.ElementTree as ET
import struct
from typing import List, Dict, Any, Optional


class ONVIFDiscovery:
    """ONVIF Device Discovery using WS-Discovery protocol.

    This class provides methods to discover ONVIF-compliant devices on the local network
    using the WS-Discovery multicast protocol.

    Attributes:
        WS_DISCOVERY_PORT (int): Default WS-Discovery port (3702)
        WS_DISCOVERY_ADDRESS_IPv4 (str): Multicast address for IPv4 discovery

    Example:
        >>> from onvif import ONVIFDiscovery
        >>> discovery = ONVIFDiscovery(timeout=5)
        >>> devices = discovery.discover()
        >>> for device in devices:
        ...     print(f"Found device at {device['host']}:{device['port']}")
    """

    WS_DISCOVERY_PORT = 3702
    WS_DISCOVERY_ADDRESS_IPv4 = "239.255.255.250"

    WS_DISCOVERY_PROBE_MESSAGE = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" '
        'xmlns:tds="http://www.onvif.org/ver10/device/wsdl" '
        'xmlns:tns="http://schemas.xmlsoap.org/ws/2005/04/discovery" '
        'xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing">'
        "<soap:Header>"
        "<wsa:Action>http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</wsa:Action>"
        "<wsa:MessageID>urn:uuid:{uuid}</wsa:MessageID>"
        "<wsa:To>urn:schemas-xmlsoap-org:ws:2005:04:discovery</wsa:To>"
        "</soap:Header>"
        "<soap:Body>"
        "<tns:Probe>"
        "<tns:Types>tds:Device</tns:Types>"
        "</tns:Probe>"
        "</soap:Body>"
        "</soap:Envelope>"
    )

    NAMESPACES = {
        "soap": "http://www.w3.org/2003/05/soap-envelope",
        "wsa": "http://schemas.xmlsoap.org/ws/2004/08/addressing",
        "wsd": "http://schemas.xmlsoap.org/ws/2005/04/discovery",
        "d": "http://schemas.xmlsoap.org/ws/2005/04/discovery",
    }

    def __init__(
        self,
        timeout: int = 4,
        interface: Optional[str] = None,
    ):
        """Initialize ONVIF Discovery.

        Args:
            timeout: Discovery timeout in seconds (default: 4)
            interface: Network interface IP to bind to (default: auto-detect)
        """
        self.timeout = timeout
        self.interface = interface
        self._local_ip = None

    def _get_local_ip(self) -> str:
        """Get local network interface IP address.

        Returns:
            str: Local IP address
        """
        if self._local_ip:
            return self._local_ip

        if self.interface:
            self._local_ip = self.interface
            return self._local_ip

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            self._local_ip = s.getsockname()[0]
            s.close()
        except Exception:
            self._local_ip = "0.0.0.0"

        return self._local_ip

    def discover(self, prefer_https: bool = False) -> List[Dict[str, Any]]:
        """Discover ONVIF devices on the network.

        Args:
            prefer_https: If True, prioritize HTTPS XAddrs when available

        Returns:
            List of discovered devices with connection information.
            Each device is a dictionary containing:
            - host (str): Device IP address or hostname
            - port (int): Device port number
            - use_https (bool): Whether device supports HTTPS
            - epr (str): Endpoint reference
            - types (list): Device types
            - scopes (list): Device scopes
            - xaddrs (list): All available XAddrs

        Example:
            >>> discovery = ONVIFDiscovery(timeout=5)
            >>> devices = discovery.discover()
            >>> for device in devices:
            ...     print(f"{device['host']}:{device['port']}")
        """
        local_ip = self._get_local_ip()

        probe_uuid = str(uuid.uuid4())
        probe = self.WS_DISCOVERY_PROBE_MESSAGE.format(uuid=probe_uuid)

        responses = []

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((local_ip, 0))
            sock.settimeout(self.timeout)

            ttl = struct.pack("b", 1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

            sock.sendto(
                probe.encode("utf-8"),
                (self.WS_DISCOVERY_ADDRESS_IPv4, self.WS_DISCOVERY_PORT),
            )

            while True:
                try:
                    data, addr = sock.recvfrom(8192)
                    response = data.decode("utf-8", errors="ignore").strip()

                    if response and len(response) > 10:
                        if response.startswith("<?xml") or response.startswith("<"):
                            responses.append({"xml": response, "address": addr[0]})

                except socket.timeout:
                    break
                except Exception:
                    # Ignore individual packet errors and continue
                    continue

            sock.close()

        except Exception:
            # Socket creation or binding failed
            return []

        # Parse responses
        return self._parse_responses(responses, prefer_https)

    def _parse_responses(
        self, responses: List[Dict[str, str]], prefer_https: bool = False
    ) -> List[Dict[str, Any]]:
        """Parse WS-Discovery responses into device information.

        Args:
            responses: List of raw XML responses
            prefer_https: If True, prioritize HTTPS XAddrs

        Returns:
            List of parsed device information
        """
        devices = []

        for resp in responses:
            try:
                device_info = self._parse_single_response(resp["xml"], prefer_https)
                if device_info and device_info.get("host"):
                    devices.append(device_info)
            except Exception:
                # Skip malformed responses
                continue

        return devices

    def _parse_single_response(
        self, xml_data: str, prefer_https: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Parse a single WS-Discovery response.

        Args:
            xml_data: Raw XML response data
            prefer_https: If True, prioritize HTTPS XAddrs

        Returns:
            Device information dictionary or None if parsing fails
        """
        try:
            root = ET.fromstring(xml_data)
            probe_match = root.find(".//d:ProbeMatch", self.NAMESPACES) or root.find(
                ".//wsd:ProbeMatch", self.NAMESPACES
            )

            if probe_match is None:
                return None

            device_info = {
                "epr": "",
                "types": [],
                "scopes": [],
                "xaddrs": [],
                "host": None,
                "port": 80,
                "use_https": False,
            }

            # Extract EPR
            epr = probe_match.find(
                ".//wsa:EndpointReference/wsa:Address", self.NAMESPACES
            )
            if epr is not None:
                device_info["epr"] = epr.text

            # Extract Types
            types_elem = probe_match.find(
                ".//d:Types", self.NAMESPACES
            ) or probe_match.find(".//wsd:Types", self.NAMESPACES)
            if types_elem is not None and types_elem.text:
                device_info["types"] = types_elem.text.split()

            # Extract Scopes
            scopes_elem = probe_match.find(
                ".//d:Scopes", self.NAMESPACES
            ) or probe_match.find(".//wsd:Scopes", self.NAMESPACES)
            if scopes_elem is not None and scopes_elem.text:
                device_info["scopes"] = scopes_elem.text.split()

            # Extract XAddrs
            xaddrs_elem = probe_match.find(
                ".//d:XAddrs", self.NAMESPACES
            ) or probe_match.find(".//wsd:XAddrs", self.NAMESPACES)
            if xaddrs_elem is not None and xaddrs_elem.text:
                device_info["xaddrs"] = xaddrs_elem.text.split()

                # Parse host, port, and protocol from XAddrs
                if device_info["xaddrs"]:
                    self._parse_xaddr(device_info, prefer_https)

            return device_info

        except Exception:
            return None

    def _parse_xaddr(
        self, device_info: Dict[str, Any], prefer_https: bool = False
    ) -> None:
        """Parse XAddr to extract host, port, and protocol.

        Args:
            device_info: Device information dictionary to update
            prefer_https: If True, prioritize HTTPS XAddrs
        """
        xaddrs = device_info.get("xaddrs", [])
        if not xaddrs:
            return

        # Select XAddr based on prefer_https flag
        if prefer_https:
            # Try to find HTTPS XAddr first
            https_xaddr = next((x for x in xaddrs if x.startswith("https://")), None)
            xaddr = https_xaddr or xaddrs[0]
        else:
            # Use first XAddr (usually HTTP)
            xaddr = xaddrs[0]

        if "://" not in xaddr:
            return

        try:
            # Detect protocol
            protocol = xaddr.split("://")[0]
            device_info["use_https"] = protocol == "https"

            # Extract host and port
            parts = xaddr.split("://")[1].split("/")[0]
            if ":" in parts:
                device_info["host"] = parts.split(":")[0]
                device_info["port"] = int(parts.split(":")[1])
            else:
                device_info["host"] = parts
                # Set default port based on protocol
                device_info["port"] = 443 if protocol == "https" else 80
        except (ValueError, IndexError):
            # Failed to parse XAddr
            pass
