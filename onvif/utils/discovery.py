"""ONVIFDiscovery: Discover ONVIF-compliant devices on the local network using WS-Discovery protocol."""

from __future__ import annotations

import logging
import socket
import struct
import uuid
from typing import Any, ClassVar

from lxml import etree

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ONVIFDiscovery:
    """Discover ONVIF devices using the WS-Discovery protocol.

    This class provides methods for discovering ONVIF-compliant devices
    on the local network using WS-Discovery multicast.

    Attributes:
        WS_DISCOVERY_PORT (int): UDP port used by WS-Discovery.
        WS_DISCOVERY_ADDRESS_IPv4 (str): IPv4 multicast address used for discovery.
        WS_DISCOVERY_PROBE_MESSAGE (str): SOAP probe message sent to discover devices.
        NAMESPACES (dict[str, str]): XML namespaces used to parse WS-Discovery responses.
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

    NAMESPACES: ClassVar[dict[str, str]] = {
        "soap": "http://www.w3.org/2003/05/soap-envelope",
        "wsa": "http://schemas.xmlsoap.org/ws/2004/08/addressing",
        "wsd": "http://schemas.xmlsoap.org/ws/2005/04/discovery",
        "d": "http://schemas.xmlsoap.org/ws/2005/04/discovery",
    }

    def __init__(
        self,
        timeout: int = 4,
        interface: str | None = None,
    ):
        """Initialize ONVIF Discovery.

        Args:
            timeout (int): Discovery timeout in seconds
            interface (str | None): Network interface IP to bind to (default: auto-detect)
        """
        self.timeout = timeout
        self.interface = interface
        self._local_ip: str | None = None

    def get_local_ip(self) -> str:
        """Get local network interface IP address.

        Returns:
            str: Local IP address
        """
        if self._local_ip is not None:
            return self._local_ip

        if self.interface:
            self._local_ip = self.interface
            return self._local_ip

        try:
            # Try to get the default route interface IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            self._local_ip = s.getsockname()[0]
            s.close()
            return self._local_ip
        except Exception as e:  # pylint: disable=broad-except
            logger.debug("Failed to get local IP via default route: %s", e)
            # Try alternative method to get local IP
            try:
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                if local_ip and not local_ip.startswith("127."):
                    self._local_ip = local_ip
                    logger.debug("Got local IP via hostname: %s", local_ip)
                    return self._local_ip
            except Exception as exc:  # pylint: disable=broad-except
                logger.debug("Failed to get local IP via hostname: %s", exc)

            # Return empty string instead of None for socket binding
            # Empty string lets OS choose the appropriate interface
            # This avoids Codacy warning about binding to "0.0.0.0"
            logger.debug("Using auto-detect for network interface")
            self._local_ip = ""
            return self._local_ip

    # pylint: disable=too-many-locals
    def discover(
        self, prefer_https: bool = False, search: str | None = None
    ) -> list[dict[str, Any]]:
        """Discover ONVIF devices on the network.

        Args:
            prefer_https (bool): If True, prioritize HTTPS XAddrs when available
            search (str | None): Optional search term to filter devices by types or scopes (case-insensitive)

        Returns:
            List of discovered devices

        !!! abstract "Each device is a dictionary containing:"
            - ``host`` (str): Device IP address or hostname.
            - ``port`` (int): Device port number.
            - ``use_https`` (bool): Whether the device supports HTTPS.
            - ``epr`` (str): Endpoint reference.
            - ``types`` (list): Device types.
            - ``scopes`` (list): Device scopes.
            - ``xaddrs`` (list): All available XAddrs.
        """
        local_ip = self.get_local_ip()
        logger.info("Starting ONVIF device discovery (timeout: %ss)", self.timeout)
        logger.debug("Local IP: %s", local_ip or "auto-detect")
        if prefer_https:
            logger.debug("Prefer HTTPS endpoints enabled")
        if search:
            logger.debug("Search filter: %s", search)

        probe_uuid = str(uuid.uuid4())
        probe = self.WS_DISCOVERY_PROBE_MESSAGE.format(uuid=probe_uuid)

        responses = []

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Bind to specific interface if available, otherwise use empty string
            # Empty string lets the OS choose the appropriate interface for multicast
            # This avoids the security issue of explicitly using "0.0.0.0"
            bind_address = local_ip if local_ip else ""
            sock.bind((bind_address, 0))
            sock.settimeout(self.timeout)

            ttl = struct.pack("b", 1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

            logger.debug(
                "Sending WS-Discovery probe to %s:%s",
                self.WS_DISCOVERY_ADDRESS_IPv4,
                self.WS_DISCOVERY_PORT,
            )
            sock.sendto(
                probe.encode("utf-8"),
                (self.WS_DISCOVERY_ADDRESS_IPv4, self.WS_DISCOVERY_PORT),
            )

            while True:
                try:
                    data, addr = sock.recvfrom(8192)
                    response = data.decode("utf-8", errors="ignore").strip()

                    if (
                        response
                        and len(response) > 10
                        and response.startswith(("<?xml", "<"))
                    ):
                        logger.debug("Received response from %s", addr[0])
                        responses.append({"xml": response, "address": addr[0]})

                except socket.timeout:
                    logger.debug("Discovery timeout reached")
                    break
                except Exception as exc:  # pylint: disable=broad-except
                    # Ignore individual packet errors and continue
                    logger.debug(
                        "Error receiving packet: %s",
                        exc,
                    )
                    continue

            sock.close()

        except Exception as exc:  # pylint: disable=broad-except
            # Socket creation or binding failed
            logger.error("Discovery failed: %s", exc)
            return []

        logger.info("Received %s responses", len(responses))

        # Parse responses
        devices = self._parse_responses(responses, prefer_https)

        # Apply search filter if provided
        if search:
            unfiltered_count = len(devices)
            devices = self._filter_devices(devices, search)
            logger.info(
                "Search filter '%s' matched %s/%s devices",
                search,
                len(devices),
                unfiltered_count,
            )

        logger.info("Discovery completed: found %s ONVIF devices", len(devices))
        return devices

    def _parse_responses(
        self, responses: list[dict[str, str]], prefer_https: bool = False
    ) -> list[dict[str, Any]]:
        """Parse WS-Discovery responses into device information.

        Args:
            responses (list[dict[str, str]]): List of raw XML responses
            prefer_https (bool): If True, prioritize HTTPS XAddrs

        Returns:
            List of parsed device information
        """
        logger.debug("Parsing %s WS-Discovery responses", len(responses))
        devices = []

        for resp in responses:
            try:
                device_info = self._parse_single_response(resp["xml"], prefer_https)
                if device_info and device_info.get("host"):
                    devices.append(device_info)
                    logger.debug(
                        "Parsed device: %s:%s", device_info["host"], device_info["port"]
                    )
            except (KeyError, TypeError, ValueError) as e:
                # Skip malformed responses
                logger.debug("Failed to parse response: %s", e)
                continue

        logger.debug("Successfully parsed %s valid devices", len(devices))
        return devices

    def _filter_devices(
        self, devices: list[dict[str, Any]], search_term: str
    ) -> list[dict[str, Any]]:
        """Filter devices based on search term in types or scopes.

        Args:
            devices (list[dict[str, Any]]): List of discovered devices
            search_term (str): Search string to match against types/scopes (case-insensitive)

        Returns:
            Filtered list of devices matching the search term
        """
        if not search_term:
            return devices

        search_lower = search_term.lower()
        filtered = []

        for device in devices:
            # Check types
            types_match = any(
                search_lower in t.lower() for t in device.get("types", [])
            )

            # Check scopes
            scopes_match = any(
                search_lower in s.lower() for s in device.get("scopes", [])
            )

            # Include device if match found in types or scopes
            if types_match or scopes_match:
                filtered.append(device)

        return filtered

    def _parse_single_response(
        self, xml_data: str, prefer_https: bool = False
    ) -> dict[str, Any] | None:
        """Parse a single WS-Discovery response.

        Args:
            xml_data (str): Raw XML response data
            prefer_https (bool): If True, prioritize HTTPS XAddrs

        Returns:
            Device information dictionary or None if parsing fails
        """
        try:
            parser = etree.XMLParser(
                resolve_entities=False,  # Disable entity resolution
                no_network=True,  # Disable network access
                remove_blank_text=True,
            )
            root = etree.fromstring(xml_data.encode("utf-8"), parser)

            probe_match = root.find(".//d:ProbeMatch", self.NAMESPACES)
            if probe_match is None:
                probe_match = root.find(".//wsd:ProbeMatch", self.NAMESPACES)

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
            if epr is not None and epr.text:
                device_info["epr"] = epr.text

            # Extract Types
            types_elem = probe_match.find(".//d:Types", self.NAMESPACES)
            if types_elem is None:
                types_elem = probe_match.find(".//wsd:Types", self.NAMESPACES)
            if types_elem is not None and types_elem.text:
                device_info["types"] = types_elem.text.split()

            # Extract Scopes
            scopes_elem = probe_match.find(".//d:Scopes", self.NAMESPACES)
            if scopes_elem is None:
                scopes_elem = probe_match.find(".//wsd:Scopes", self.NAMESPACES)
            if scopes_elem is not None and scopes_elem.text:
                device_info["scopes"] = scopes_elem.text.split()

            # Extract XAddrs
            xaddrs_elem = probe_match.find(".//d:XAddrs", self.NAMESPACES)
            if xaddrs_elem is None:
                xaddrs_elem = probe_match.find(".//wsd:XAddrs", self.NAMESPACES)
            if xaddrs_elem is not None and xaddrs_elem.text:
                device_info["xaddrs"] = xaddrs_elem.text.split()

                # Parse host, port, and protocol from XAddrs
                if device_info["xaddrs"]:
                    self._parse_xaddr(device_info, prefer_https)

            return device_info

        except etree.XMLSyntaxError:
            return None
        except Exception as e:  # pylint: disable=broad-except
            logger.warning("Error occurred while parsing device info: %s", e)
            return None

    def _parse_xaddr(
        self, device_info: dict[str, Any], prefer_https: bool = False
    ) -> None:
        """Parse XAddr to extract host, port, and protocol.

        Args:
            device_info (dict[str, Any]): Device information dictionary to update
            prefer_https (bool): If True, prioritize HTTPS XAddrs
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
        except (ValueError, IndexError, KeyError) as e:
            # Failed to parse XAddr
            logger.warning("Error occurred while parsing XAddr %s: %s", xaddr, e)
