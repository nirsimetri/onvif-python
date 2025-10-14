"""
Path: examples/error_handling.py
Author: @kaburagisec
Created: October 14, 2025
Tested devices: TP-Link Tapo C210 (https://www.tp-link.com/en/home-networking/cloud-camera/tapo-c210/)

This example demonstrates various ways to handle ONVIF operation errors,
especially dealing with ActionNotSupported errors from devices that don't
support certain features.

Applied for (>= v0.0.7 patch)
"""

from onvif import ONVIFClient, CacheMode, ONVIFErrorHandler, ONVIFOperationException

HOST = "192.168.1.14"
PORT = 2020
USERNAME = "admintapo"
PASSWORD = "admin123"


def example_1_safe_call():
    """
    Example 1: Using safe_call utility
    
    safe_call automatically handles ActionNotSupported errors and returns
    a default value instead of raising an exception.
    """
    print("=" * 60)
    print("Example 1: Using safe_call")
    print("=" * 60)
    
    client = ONVIFClient(HOST, PORT, USERNAME, PASSWORD, cache=CacheMode.NONE)
    device = client.devicemgmt()
    
    # Returns None if operation is not supported
    ip_filter = ONVIFErrorHandler.safe_call(lambda: device.GetIPAddressFilter())
    if ip_filter:
        print(f"✓ IP Address Filter: {ip_filter}")
    else:
        print("⚠ GetIPAddressFilter not supported or returned None")
    
    # Returns empty list if operation is not supported
    dns_info = ONVIFErrorHandler.safe_call(
        lambda: device.GetDNS(),
        default={"FromDHCP": False, "DNSManual": []}
    )
    print(f"✓ DNS Info: {dns_info}")
    
    print()


def example_2_decorator():
    """
    Example 2: Using @ignore_unsupported decorator
    
    The decorator wraps a function to automatically handle ActionNotSupported
    errors and return None instead.
    """
    print("=" * 60)
    print("Example 2: Using @ignore_unsupported decorator")
    print("=" * 60)
    
    client = ONVIFClient(HOST, PORT, USERNAME, PASSWORD, cache=CacheMode.NONE)
    device = client.devicemgmt()
    
    @ONVIFErrorHandler.ignore_unsupported
    def get_zero_configuration():
        return device.GetZeroConfiguration()
    
    @ONVIFErrorHandler.ignore_unsupported
    def get_ntp():
        return device.GetNTP()
    
    zero_conf = get_zero_configuration()
    if zero_conf:
        print(f"✓ Zero Configuration: {zero_conf}")
    else:
        print("⚠ GetZeroConfiguration not supported")
    
    ntp = get_ntp()
    if ntp:
        print(f"✓ NTP: {ntp}")
    else:
        print("⚠ GetNTP not supported")
    
    print()


def example_3_manual_handling():
    """
    Example 3: Manual exception handling
    
    For more fine-grained control, catch ONVIFOperationException and use
    is_action_not_supported() to check the error type.
    """
    print("=" * 60)
    print("Example 3: Manual exception handling")
    print("=" * 60)
    
    client = ONVIFClient(HOST, PORT, USERNAME, PASSWORD, cache=CacheMode.NONE)
    device = client.devicemgmt()
    
    # Try GetSystemUris (not always supported), fallback to alternative
    try:
        system_uris = device.GetSystemUris()
        print(f"✓ System URIs:")
        
        # System Log URIs (can be multiple)
        if hasattr(system_uris, 'SystemLogUris') and system_uris.SystemLogUris:
            log_uris = system_uris.SystemLogUris
            if hasattr(log_uris, 'SystemLog'):
                logs = log_uris.SystemLog if isinstance(log_uris.SystemLog, list) else [log_uris.SystemLog]
                for log in logs:
                    log_type = getattr(log, 'Type', 'Unknown')
                    log_uri = getattr(log, 'Uri', 'N/A')
                    print(f"  System Log ({log_type}): {log_uri}")
        
        # Support Info URI
        if hasattr(system_uris, 'SupportInfoUri') and system_uris.SupportInfoUri:
            print(f"  Support Info: {system_uris.SupportInfoUri}")
        
        # System Backup URI
        if hasattr(system_uris, 'SystemBackupUri') and system_uris.SystemBackupUri:
            print(f"  System Backup: {system_uris.SystemBackupUri}")
            
    except ONVIFOperationException as e:
        if ONVIFErrorHandler.is_action_not_supported(e):
            print("⚠ GetSystemUris not supported by this device")
            print("  Using alternative method to get device info...")
            
            # Fallback: Get basic device information
            device_info = device.GetDeviceInformation()
            print(f"✓ Device Information (alternative):")
            print(f"  Manufacturer: {getattr(device_info, 'Manufacturer', 'N/A')}")
            print(f"  Model: {getattr(device_info, 'Model', 'N/A')}")
            print(f"  FirmwareVersion: {getattr(device_info, 'FirmwareVersion', 'N/A')}")
        else:
            # Other errors should be re-raised
            print(f"✗ Unexpected error: {e}")
            raise
    
    print()


def example_4_batch_operations():
    """
    Example 4: Batch operations with graceful degradation
    
    Query multiple device features, collecting what's available and
    gracefully handling unsupported operations.
    """
    print("=" * 60)
    print("Example 4: Batch operations with graceful degradation")
    print("=" * 60)
    
    client = ONVIFClient(HOST, PORT, USERNAME, PASSWORD, cache=CacheMode.NONE)
    device = client.devicemgmt()
    
    # Define operations to try
    operations = {
        "Device Info": lambda: device.GetDeviceInformation(),
        "System Date/Time": lambda: device.GetSystemDateAndTime(),
        "Network Interfaces": lambda: device.GetNetworkInterfaces(),
        "Hostname": lambda: device.GetHostname(),
        "DNS": lambda: device.GetDNS(),
        "NTP": lambda: device.GetNTP(),
        "Network Protocols": lambda: device.GetNetworkProtocols(),
        "IP Address Filter": lambda: device.GetIPAddressFilter(),
        "Zero Configuration": lambda: device.GetZeroConfiguration(),
        "Services": lambda: device.GetServices(IncludeCapability=False),
    }
    
    results = {}
    supported_count = 0
    unsupported_count = 0
    
    for name, operation in operations.items():
        result = ONVIFErrorHandler.safe_call(operation, default=None, log_error=False)
        results[name] = result
        
        if result is not None:
            print(f"✓ {name}: Available")
            supported_count += 1
        else:
            print(f"⚠ {name}: Not supported")
            unsupported_count += 1
    
    print(f"\nSummary: {supported_count} supported, {unsupported_count} not supported")
    print()


def example_5_critical_operations():
    """
    Example 5: Critical operations that should not be ignored
    
    Some operations are critical and should fail loudly if not supported.
    Use ignore_unsupported=False for these.
    """
    print("=" * 60)
    print("Example 5: Critical operations (don't ignore errors)")
    print("=" * 60)
    
    client = ONVIFClient(HOST, PORT, USERNAME, PASSWORD, cache=CacheMode.NONE)
    device = client.devicemgmt()
    
    # Critical operation - must succeed
    try:
        device_info = ONVIFErrorHandler.safe_call(
            lambda: device.GetDeviceInformation(),
            ignore_unsupported=False  # Raise exception if not supported
        )
        print(f"✓ Device Info (critical):")
        print(f"  Manufacturer: {getattr(device_info, 'Manufacturer', 'N/A')}")
        print(f"  Model: {getattr(device_info, 'Model', 'N/A')}")
        print(f"  FirmwareVersion: {getattr(device_info, 'FirmwareVersion', 'N/A')}")
    except ONVIFOperationException as e:
        print(f"✗ Critical operation failed: {e}")
        print("  Cannot continue without device information!")
        return
    
    print()


def main():
    """Run all examples"""
    try:
        example_1_safe_call()
        example_2_decorator()
        example_3_manual_handling()
        example_4_batch_operations()
        example_5_critical_operations()
        
        print("=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
