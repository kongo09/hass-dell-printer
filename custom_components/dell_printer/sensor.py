from homeassistant.components.sensor import SensorEntity

import logging

from . import DellPrinter
from .constants import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    entities = []
    coordinator = hass.data[DOMAIN][entry.entry_id]

    if coordinator.api.can_bridge():
        entities.append(BridgeWifiVersion(coordinator))
        entities.append(BridgeVersion(coordinator))

    async_add_entities(entities)
    return True


class BridgeWifiVersion(DellPrinter, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.set_id("wifi_version")
        self.set_name("WiFi Firmware Version")

    @property
    def state(self):
        versions = self.data.get("versions", {})
        return versions.get("wifiFirmwareVersion")

    @property
    def entity_category(self):
        return "diagnostic"


class BridgeVersion(DellPrinter, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.set_id("version")
        self.set_name("Firmware Version")

    @property
    def state(self):
        versions = self.data.get("versions", {})
        return versions.get("firmwareVersion")

    @property
    def entity_category(self):
        return "diagnostic"

