"""Expose only wireless metrics supported by both SSH and HTTP backends."""
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfDataRate
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

# Only include metrics normalised by both coordinator backends.
COMMON_SENSORS = {
    "signal": ("Wireless Signal", "dBm", SensorDeviceClass.SIGNAL_STRENGTH, SensorStateClass.MEASUREMENT),
    "noise": ("Wireless Noise", "dBm", SensorDeviceClass.SIGNAL_STRENGTH, SensorStateClass.MEASUREMENT),
    "ccq": ("Wireless CCQ", PERCENTAGE, None, SensorStateClass.MEASUREMENT),
    "snr": ("Wireless SNR", "dB", None, SensorStateClass.MEASUREMENT),
    "wlanTxRate": ("Wireless Transmit Rate", UnitOfDataRate.MEGABITS_PER_SECOND, None, None),
    "wlanRxRate": ("Wireless Receive Rate", UnitOfDataRate.MEGABITS_PER_SECOND, None, None),
}


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        AirOSCommonSensor(coordinator, entry, key, *details)
        for key, details in COMMON_SENSORS.items()
        if (coordinator.data or {}).get(key) is not None
    ]
    async_add_entities(entities)


class AirOSCommonSensor(CoordinatorEntity, SensorEntity):
    """A sensor backed by a metric shared by both connection modes."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, key, label, unit, device_class, state_class):
        super().__init__(coordinator)
        self.key = key
        self._attr_name = label
        self._attr_unique_id = f"{entry.data['host']}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.data["host"])},
            name=entry.data["name"],
            manufacturer="Ubiquiti",
            model=(coordinator.data or {}).get("device_model") or "Ubiquiti AirOS",
            configuration_url=coordinator.host.rstrip("/"),
        )

    @property
    def native_value(self):
        value = (self.coordinator.data or {}).get(self.key)
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return str(value)[:255]
