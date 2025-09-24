import nmap
import requests
import json
import argparse


def is_onvif(ip, port, timeout=3):
    url = f"http://{ip}:{port}/onvif/service"
    headers = {"Content-Type": "application/soap+xml; charset=utf-8"}

    soap_body = """<?xml version="1.0" encoding="utf-8"?>
    <s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
                xmlns:tds="http://www.onvif.org/ver10/device/wsdl">
        <s:Body>
            <tds:GetCapabilities/>
        </s:Body>
    </s:Envelope>"""

    try:
        r = requests.post(url, data=soap_body, headers=headers, timeout=timeout)

        if r.status_code in (200, 401, 405, 400, 500):
            ctype = r.headers.get("Content-Type", "").lower()
            text = r.text.lower()

            if "xml" in ctype or "soap" in ctype or "onvif" in text:
                return True
        return False
    except Exception:
        return False


def scan_onvif_devices(subnet="192.168.1.0/24", ports="1-10000"):
    nm = nmap.PortScanner()
    # print(f"Scanning {subnet} on ports {ports} ...")
    nm.scan(hosts=subnet, arguments=f"-p {ports} -T4")

    results = {}
    for host in nm.all_hosts():
        for proto in nm[host].all_protocols():
            lport = nm[host][proto].keys()
            for port in lport:
                if is_onvif(host, port):
                    if host not in results:
                        results[host] = []
                    results[host].append(port)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ONVIF Device Scanner")
    parser.add_argument(
        "--subnet", type=str, required=False, default="192.168.1.0/24", help="Subnet"
    )
    args = parser.parse_args()

    try:
        # print(is_onvif("192.168.1.3", 80))
        results = scan_onvif_devices(args.subnet)
        print(json.dumps(results, indent=4))
    except Exception as e:
        print(e)
