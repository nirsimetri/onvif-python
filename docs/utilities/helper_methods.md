Every ONVIF service provides **four** essential helper methods to improve the development experience and make working with ONVIF operations more intuitive:

!!! info
    These helper methods are available on **all** ONVIF services (`devicemgmt()`, `media()`, `ptz()`, `events()`, `imaging()`, `analytics()`, etc.) and provide a consistent API for exploring and using ONVIF capabilities across different device types and manufacturers.

### `type(type_name)`

Creates and returns an instance of the specified ONVIF type for building complex request parameters (applied at [`>=v0.1.9`](../releases.md/#v0.1.9)).

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

Lists all available operations for the current service (applied at [`>=v0.2.0`](../releases.md/#v0.2.0)).

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

Provides comprehensive documentation and parameter information for any ONVIF operation (applied at [`>=v0.2.0`](../releases.md/#v0.2.0)).

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

### `to_dict(zeep_object)`

Converts a Zeep object (the raw result returned from ONVIF operations) into a native Python dictionary that is easy to serialize, inspect, and manipulate (applied at [`>=v0.2.9`](../releases.md/#v0.2.9)).

**Returns:**

- Python `dict` representation of the Zeep object. Returns an empty dict `{}` if `zeep_object` is `None` or if conversion fails for any reason.

**Usage:**
```python
device = client.devicemgmt()
media = client.media()
ptz = client.ptz()

# Convert device information result to dictionary
info = device.GetDeviceInformation()
info_dict = device.to_dict(info)
print("Manufacturer:", info_dict["Manufacturer"])
print("Model:", info_dict["Model"])
print("FirmwareVersion:", info_dict["FirmwareVersion"])

# Convert media profiles (usually a list of complex objects)
profiles = media.GetProfiles()
profiles_dict = media.to_dict(profiles)
for profile in profiles_dict:
    print(f"Profile: {profile.get('Name')} (token={profile.get('token')})")

# Convert PTZ configuration
configs = ptz.GetConfigurations()
configs_dict = ptz.to_dict(configs)
print(f"Found {len(configs_dict)} PTZ configurations")

# Safe handling of None results
empty_result = None
safe_dict = device.to_dict(empty_result)  # Returns {}
assert safe_dict == {}
```