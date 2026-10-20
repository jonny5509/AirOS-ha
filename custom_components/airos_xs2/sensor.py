"""Dispatch sensors to the backend selected for this config entry."""
from . import sensor_http, sensor_ssh


async def async_setup_entry(hass, entry, async_add_entities):
    protocol = entry.data.get("protocol")
    if protocol is None:
        protocol = "http" if entry.data.get("host", "").lower().startswith(("http://", "https://")) else "ssh"
    if protocol.lower() == "ssh":
        await sensor_ssh.async_setup_entry(hass, entry, async_add_entities)
    else:
        await sensor_http.async_setup_entry(hass, entry, async_add_entities)
