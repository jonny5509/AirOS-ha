"""Maintenance controls for legacy airOS devices over SSH or HTTP."""
import asyncssh
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AirOSRebootButton(coordinator, entry)])


class AirOSRebootButton(CoordinatorEntity, ButtonEntity):
    """Button to reboot the device without factory-resetting it."""

    _attr_has_entity_name = True
    _attr_name = "Reboot"
    _attr_icon = "mdi:restart"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data['host']}_reboot"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.data["host"])},
            manufacturer="Ubiquiti",
            model="Ubiquiti AirOS",
            name=entry.data["name"],
            configuration_url=coordinator.host.rstrip("/"),
        )
        self._coordinator = coordinator

    async def async_press(self):
        """Reboot through the configured transport."""
        if hasattr(self._coordinator, "async_reboot"):
            await self._coordinator.async_reboot()
            return

        async with asyncssh.connect(
            self._coordinator.host,
            username=self._coordinator.username,
            password=self._coordinator.password,
            known_hosts=None,
            kex_algs=["diffie-hellman-group1-sha1"],
            encryption_algs=["aes128-cbc"],
            server_host_key_algs=["ssh-rsa"],
        ) as conn:
            await conn.run("reboot")
