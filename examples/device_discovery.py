import socket
import time
import platform
from typing import Dict, List, Optional

import urllib3
from scapy.all import sniff, UDP, Raw, conf, get_windows_if_list

from .models import ONVIFDevice
from .soap import SOAPMessageBuilder, SOAPParser
from .utils import Logger

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ONVIFDiscovery:
    """Cross-platform ONVIF device discovery (UDP or Scapy fallback)."""

    MULTICAST_ADDRESS = "239.255.255.250"
    MULTICAST_PORT = 3702

    def __init__(self, timeout: int = 4, retries: int = 2, use_scapy: Optional[bool] = None):
        self.timeout = timeout
        self.retries = retries

        # Auto-enable Scapy on Windows (Winsock bug workaround)
        if use_scapy is None:
            self.use_scapy = platform.system() == "Windows"
        else:
            self.use_scapy = use_scapy

        # Configure Scapy for packet capture
        if self.use_scapy:
            conf.use_pcap = True
            conf.ipv6_enabled = False

    # -------------------------------------------------------------------------
    # Base UDP methods
    # -------------------------------------------------------------------------
    def _create_discovery_socket(self) -> socket.socket:
        """Create and configure socket for discovery"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 512000)
        sock.settimeout(self.timeout)
        sock.bind(("", self.MULTICAST_PORT))
        return sock

    def _send_probe(self, sock: socket.socket) -> None:
        """Send WS-Discovery probe message"""
        try:
            probe_message = SOAPMessageBuilder.create_discovery_probe()
            sock.sendto(probe_message.encode(), (self.MULTICAST_ADDRESS, self.MULTICAST_PORT))
            Logger.debug("Sent discovery probe message")
            time.sleep(0.1)
        except Exception as e:
            Logger.error(f"Error sending probe message: {str(e)}")
            raise

    def _collect_responses_udp(self, sock: socket.socket) -> List[Dict]:
        """Collect and parse responses via UDP socket (Linux/macOS reliable)"""
        responses = []
        seen_ips = set()
        while True:
            try:
                data, addr = sock.recvfrom(8192)
                ip_address = addr[0]
                if ip_address in seen_ips:
                    continue

                xml_data = data.decode("utf-8", errors="ignore")
                parsed = SOAPParser.parse_discovery_response(xml_data)
                if parsed and parsed["urls"]:
                    seen_ips.add(ip_address)
                    parsed["address"] = ip_address
                    responses.append(parsed)
                    Logger.success(f"Found device at {ip_address}")
            except socket.timeout:
                break
            except Exception as e:
                Logger.error(f"Error processing UDP response: {str(e)}")
                continue
        return responses

    # -------------------------------------------------------------------------
    # Scapy mode (for Windows)
    # -------------------------------------------------------------------------
    def _get_iface_for_ip(self, ip: str) -> Optional[str]:
        """Find correct Npcap interface name for given IP"""
        try:
            for iface in get_windows_if_list():
                if ip in iface.get("ips", []) and "Npcap Packet Driver" in iface["name"]:
                    return iface["name"]
        except Exception:
            return None
        return None

    def _collect_responses_scapy(self, local_ip: str) -> List[Dict]:
        """Collect responses using Scapy (Npcap driver)"""
        responses = []
        seen = set()

        iface = self._get_iface_for_ip(local_ip)
        if not iface:
            Logger.warning("No suitable Npcap interface found, fallback to UDP mode.")
            self.use_scapy = False
            return []

        Logger.debug(f"Using Scapy interface: {iface}")

        def _process(pkt):
            if pkt.haslayer(UDP) and pkt.haslayer(Raw):
                payload = bytes(pkt[Raw])
                if b"ProbeMatches" not in payload:
                    return
                try:
                    xml_start = payload.find(b"<?xml")
                    xml_data = payload[xml_start:].decode("utf-8", errors="ignore")
                    parsed = SOAPParser.parse_discovery_response(xml_data)
                    if parsed and parsed["urls"]:
                        # Try to extract sender IP
                        ip_src = pkt[IP].src if pkt.haslayer("IP") else "unknown"
                        if ip_src not in seen:
                            seen.add(ip_src)
                            parsed["address"] = ip_src
                            responses.append(parsed)
                            Logger.success(f"Found device (Scapy) at {ip_src}")
                except Exception as e:
                    Logger.error(f"Scapy parse error: {e}")

        from scapy.all import IP
        sniff(
            iface=iface,
            filter=f"udp and port {self.MULTICAST_PORT}",
            timeout=self.timeout,
            prn=_process,
            store=False,
        )
        return responses

    # -------------------------------------------------------------------------
    # Unified discovery entry point
    # -------------------------------------------------------------------------
    def discover(self) -> List[ONVIFDevice]:
        """Perform ONVIF WS-Discovery with retry and platform adaptation"""
        Logger.header("Starting ONVIF device discovery...")
        devices: Dict[str, ONVIFDevice] = {}
        local_ip = socket.gethostbyname(socket.gethostname())

        for attempt in range(self.retries):
            if attempt > 0:
                Logger.info(f"Retry attempt {attempt + 1}/{self.retries}")

            try:
                if self.use_scapy:
                    Logger.debug("Using Scapy-based discovery...")
                    responses = self._collect_responses_scapy(local_ip)
                else:
                    with self._create_discovery_socket() as sock:
                        self._send_probe(sock)
                        time.sleep(0.5)
                        responses = self._collect_responses_udp(sock)

                for resp in responses:
                    addr = resp["address"]
                    if addr not in devices:
                        devices[addr] = ONVIFDevice(
                            address=addr,
                            urls=resp["urls"],
                            types=resp["types"],
                        )

            except Exception as e:
                Logger.error(f"Discovery error on attempt {attempt + 1}: {str(e)}")
                if attempt < self.retries - 1:
                    time.sleep(1)
                continue

        # Summary
        if devices:
            Logger.success(f"\nDiscovery completed: Found {len(devices)} device(s)")
            if Logger.DEBUG:
                for d in devices.values():
                    Logger.debug(f"\nDevice details:\n{d}")
        else:
            Logger.warning("\nNo ONVIF devices found on the network")

        return list(devices.values())

    def estimate_discovery_time(self) -> float:
        base = self.timeout
        retry = base * self.retries
        return base + retry + 0.5
