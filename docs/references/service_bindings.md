ONVIF services are defined by WSDL bindings. In this library, there are two main patterns:

### Single Binding Services

Most ONVIF services use a single binding, mapping directly to one endpoint. These are accessed via simple client methods, and the binding/xAddr is always known from device services or capabilities.

#### Examples

```python
client.devicemgmt()   # DeviceBinding
client.media()        # MediaBinding
client.ptz()          # PTZBinding
...
```

These are considered fixed and always accessed directly.

### Multi-Binding Services

Some ONVIF services have multiple bindings in the same WSDL. These typically include:
- A **root binding** (main entry point)
- One or more **sub-bindings**, discovered or created dynamically (e.g. after subscription/configuration creation)

#### Examples

1. **Events**
   - **Root:** `EventBinding`
   - **Sub-bindings:**
     - `PullPointSubscriptionBinding` (created via `CreatePullPointSubscription`)
     - `SubscriptionManagerBinding` (manages existing subscriptions)
     - `NotificationProducerBinding`

   Usage in library:
   ```python
   client.events()                    # root binding
   client.pullpoint(subscription)     # sub-binding (dynamic, via SubscriptionReference.Address)
   client.subscription(subscription)  # sub-binding (dynamic, via SubscriptionReference.Address)
   client.notification()              # sub-binding accessor
   ```

2. **Security (Advanced Security)**
   - **Root:** `AdvancedSecurityServiceBinding`
   - **Sub-bindings:**
     - `JWTBinding`
     - `AuthorizationServerBinding`
     - `KeystoreBinding`
     - `Dot1XBinding`
     - `TLSServerBinding`
     - `MediaSigningBinding`

   Usage in library:
   ```python
   client.security()                  # root binding
   client.jwt()                       # sub-binding accessor
   client.authorizationserver()       # ..
   client.keystore()
   client.dot1x()
   client.tlsserver()
   client.mediasigning()
   ```

3. **Analytics**
   - **Root:** `AnalyticsEngineBinding`
   - **Sub-bindings:**
     - `RuleEngineBinding`

   Usage in library:
   ```python
   client.analytics()   # root binding
   client.ruleengine()  # sub-binding accessor
   ```

### Summary

- **Single binding services:** Always accessed directly (e.g. `client.media()`).
- **Multi-binding services:** Have a root + sub-binding(s). Root is fixed; sub-bindings may require dynamic creation or explicit xAddr (e.g. `client.pullpoint(subscription)`, `client.authorizationserver(xaddr)`).