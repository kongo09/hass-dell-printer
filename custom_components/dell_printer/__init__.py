from __future__ import annotations
from .dell import DellCoordinator
from .const import DOMAIN, PLATFORMS

from homeassistant.core import HomeAssistant
from homeassistant.helpers import service

# from homeassistant.helpers import device_registry
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    data = entry.as_dict()["data"]
    _LOGGER.debug(f"async_setup_entry: {data}")

    coordinator = DellCoordinator(hass, entry, data)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    for p in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, p))
    return True


async def async_unload_entry(hass: HomeAssistant, entry):
    await hass.data[DOMAIN][entry.entry_id].unload()
    for p in PLATFORMS:
        await hass.config_entries.async_forward_entry_unload(entry, p)
    hass.data[DOMAIN].pop(entry.entry_id)
    return True


async def async_setup(hass: HomeAssistant, config) -> bool:
    hass.data[DOMAIN] = dict()
    return True


class DellPrinter(CoordinatorEntity):
    def set_id(self, suffix: str):
        self.id_suffix = suffix

    def set_name(self, name: str):
        self.name_suffix = name

    @property
    def name(self) -> str:
        return "Dell Printer %s" % (self.name_suffix)

    @property
    def unique_id(self) -> str:
        return "dell-printer-%s-%s" % (self.get_id, self.id_suffix)

    @property
    def data(self) -> dict:
        return self.coordinator.data.get("bridge_info", {})

    @property
    def get_id(self):
        return self.data.get("ids", {}).get("hardwareId")

    @property
    def device_info(self):
        model = "Hardware Bridge" if self.data.get(
            "bridgeType", 1) else "Software Bridge"
        versions = self.data.get("versions", {})
        return {
            "identifiers": {("id", self.get_id)},
            "name": "Dell Printer",
            "manufacturer": "Dell",
            "model": model,
            "sw_version": versions.get("firmwareVersion"),
        }
