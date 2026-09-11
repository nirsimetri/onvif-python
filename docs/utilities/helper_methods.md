Every ONVIF service provides three essential helper methods to improve the development experience and make working with ONVIF operations more intuitive:

!!! info
    These helper methods are available on **all** ONVIF services (`devicemgmt()`, `media()`, `ptz()`, `events()`, `imaging()`, `analytics()`, etc.) and provide a consistent API for exploring and using ONVIF capabilities across different device types and manufacturers.

### `type(type_name)`

Creates and returns an instance of the specified ONVIF type for building complex request parameters (applied at [`>=v0.1.9`](https://github.com/nirsimetri/onvif-python/releases/tag/v0.1.9)).

**Usage:**
```python
device = client.devicemgmt()

# Create a new user object
new_user = device.type('CreateUsers')
new_user.User.append({
    "Username": 'new_user', 
    "Password": 'new_password', 
    "UserLevel": 'User'
})
device.CreateUsers(new_user)

# Set hostname
hostname = device.type('SetHostname')
hostname.Name = 'NewHostname'
device.SetHostname(hostname)

# Configure system time
time_params = device.type('SetSystemDateAndTime')
time_params.DateTimeType = 'NTP'
time_params.DaylightSavings = True
time_params.TimeZone.TZ = 'UTC+02:00'
now = datetime.now()
time_params.UTCDateTime.Date.Year = now.year
time_params.UTCDateTime.Date.Month = now.month
time_params.UTCDateTime.Date.Day = now.day
time_params.UTCDateTime.Time.Hour = now.hour
time_params.UTCDateTime.Time.Minute = now.minute
time_params.UTCDateTime.Time.Second = now.second
device.SetSystemDateAndTime(time_params)
```

### `operations()`

Lists all available operations for the current service (applied at [`>=v0.2.0`](https://github.com/nirsimetri/onvif-python/releases/tag/v0.2.0)).

**Returns:**

- List of operation names that can be called on the service

**Usage:**
```python
device = client.devicemgmt()
media = client.media()
ptz = client.ptz()

# List all available operations for each service
print("Device Management Operations:")
for op in device.operations():
    print(f"  - {op}")

print("\nMedia Operations:")
for op in media.operations():
    print(f"  - {op}")

print("\nPTZ Operations:")
for op in ptz.operations():
    print(f"  - {op}")

# Check if specific operation is supported
if 'ContinuousMove' in ptz.operations():
    print("PTZ continuous movement is supported")
```

### `desc(method_name)`

Provides comprehensive documentation and parameter information for any ONVIF operation (applied at [`>=v0.2.0`](https://github.com/nirsimetri/onvif-python/releases/tag/v0.2.0)).

**Returns:**

- `doc`: Method documentation from WSDL
- `required`: List of required parameter names
- `optional`: List of optional parameter names
- `method_name`: The method name
- `service_name`: The service name

**Usage:**
```python
device = client.devicemgmt()

# Get detailed information about a method
info = device.desc('GetDeviceInformation')
print(info['doc'])
print("Required params:", info['required'])
print("Optional params:", info['optional'])

# Explore available methods first
methods = device.operations()
for method in methods[:5]:  # Show first 5 methods
    info = device.desc(method)
    print(f"{method}: {len(info['required'])} required, {len(info['optional'])} optional")
```