"""Expose only sensor entities backed by fields shared across SSH and HTTP."""
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import PERCENTAGE
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

# Canonical field names are produced by both coordinator implementations.
# Optional metrics are only created when a real value is present.
SENSORS = {
    # Main device
    "uptime_seconds": ("Uptime", "s", "main", SensorDeviceClass.DURATION, None),
    "ip_address": ("Device IP Address", None, "main", None, None),
    # Ethernet interface
    "ethernet_mac": ("Ethernet MAC Address", None, "ethernet", None, None),
    "ethernet_interface_state": ("Ethernet Interface State", None, "ethernet", None, None),
    "ethernet_rx_bytes": ("Ethernet Bytes Received", "B", "ethernet", SensorDeviceClass.DATA_SIZE, SensorStateClass.TOTAL_INCREASING),
    "ethernet_tx_bytes": ("Ethernet Bytes Sent", "B", "ethernet", SensorDeviceClass.DATA_SIZE, SensorStateClass.TOTAL_INCREASING),
    # Wireless interface
    "signal": ("Wireless Signal", "dBm", "wireless", SensorDeviceClass.SIGNAL_STRENGTH, SensorStateClass.MEASUREMENT),
    "noise": ("Wireless Noise", "dBm", "wireless", SensorDeviceClass.SIGNAL_STRENGTH, SensorStateClass.MEASUREMENT),
    "ccq": ("Wireless CCQ", PERCENTAGE, "wireless", None, SensorStateClass.MEASUREMENT),
    "snr": ("Wireless SNR", "dB", "wireless", None, SensorStateClass.MEASUREMENT),
    "wlanTxRate": ("Wireless Transmit Rate", "Mbit/s", "wireless", None, None),
    "wlanRxRate": ("Wireless Receive Rate", "Mbit/s", "wireless", None, None),
}


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    data = coordinator.data or {}
    host = entry.data["host"]
    name = entry.data["name"]
    entities = []
    for key, (label, unit, kind, device_class, state_class) in SENSORS.items():
        value = data.get(key)
        if value is None or value == "":
            continue
        entities.append(
            AirOSCommonSensor(
                coordinator, entry, key, label, unit, kind, device_class, state_class
            )
        )
    async_add_entities(entities)


class AirOSCommonSensor(CoordinatorEntity, SensorEntity):
    """Sensor whose data key is normalised by both connection backends."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, key, label, unit, kind, device_class, state_class):
        super().__init__(coordinator)
        self.key = key
        self.kind = kind
        self._attr_name = label
        self._attr_unique_id = f"{entry.data['host']}_{key}"
        if unit:
            self._attr_native_unit_of_measurement = unit
        if device_class:
            self._attr_device_class = device_class
        if state_class:
            self._attr_state_class = state_class

        host = entry.data["host"]
        if kind == "main":
            identifiers = {(DOMAIN, host)}
            device_name = entry.data["name"]
            via_device = None
        else:
            identifiers = {(DOMAIN, f"{host}_{kind}")}
            device_name = f"{entry.data['name']} {kind.capitalize()}"
            via_device = (DOMAIN, host)
        self._attr_device_info = DeviceInfo(
            identifiers=identifiers,
            name=device_name,
            manufacturer="Ubiquiti",
            model=(coordinator.data or {}).get("device_model") or "Ubiquiti AirOS",
            via_device=via_device,
            configuration_url=coordinator.host.rstrip("/"),
        )

    @property
    def native_value(self):
        value = (self.coordinator.data or {}).get(self.key)
        if value is None:
            return None
        if self.key in {
            "uptime_seconds", "ethernet_rx_bytes", "ethernet_tx_bytes",
            "signal", "noise", "ccq", "snr", "wlanTxRate", "wlanRxRate",
        }:
            try:
                return float(value)
            except (TypeError, ValueError):
                return None
        return str(value)[:255]
