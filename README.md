# Ubiquiti AirOS (SSH / HTTP / HTTPS)

Home Assistant custom integration for legacy Ubiquiti airOS devices. Select **SSH**, **HTTP**, or **HTTPS** during setup.

## Features

- One integration and one setup flow for SSH, HTTP, and HTTPS connections.
- Shared sensor platform with available readings grouped under Main, Ethernet, and Wireless devices.
- HTTPS preserves the selected URL scheme and uses normal TLS certificate verification.
- Sensor availability depends on the data exposed by the device firmware.

## Installation

### HACS

1. Add `https://github.com/jonny5509/AirOS-ha` as a custom repository in HACS.
2. Choose **Integration**, install it, and restart Home Assistant.
3. Add **Ubiquiti AirOS** from Settings → Devices & services.
4. Choose SSH, HTTP, or HTTPS and enter the device details.

### Manual

Copy `custom_components/airos_xs2` into `/config/custom_components/`, restart Home Assistant, and add **Ubiquiti AirOS**.

## Connection methods

### SSH

Uses `asyncssh` and legacy SSH algorithms for older airOS firmware. SSH can provide richer telemetry, depending on firmware and device configuration. Enable SSH on the device.

### HTTP

Uses the legacy airOS web interface without encryption. HTTP does not encrypt credentials or telemetry; use only on a trusted LAN or VPN and never expose the management interface directly to the public internet.

### HTTPS

Uses the device's HTTPS web interface. TLS certificate verification remains enabled by default, so devices with self-signed or otherwise untrusted certificates may fail to connect until their certificate is trusted.

## Migration notes

The integration domain remains `airos_xs2`. Existing entries should retain their configured connection method. After updating, check each device's entities and confirm the selected connection method.

## Compatibility

Officially supported hardware is limited to the original Ubiquiti NanoStation 2 (NS2/XS2) and NanoStation 5 (NS5/XS5), running legacy airOS 3.x–4.x.

NanoStation Loco, Bullet, PicoStation, PowerStation, and other product families are **not officially supported**. Device identification or parsing of similar status fields does not establish compatibility.

Available sensors depend on the radio model, firmware, connection method, and fields or commands exposed by the device. The compatibility statement is a supported-scope baseline, not a claim that every firmware build has been verified on physical hardware.

## License

MIT
