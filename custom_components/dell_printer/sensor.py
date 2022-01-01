from custom_components.dell_printer import DellDataUpdateCoordinator
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

import logging

from .const import DOMAIN, PRINTER_PRINT_VOLUME

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    entities = []
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities.append(PrintVolume(coordinator))
    
    async_add_entities(entities, True)
    return True


class PrintVolume(CoordinatorEntity):
    """Representation of a sensor."""

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        super().__init__(coordinator)
        self.attrs = {}
        # self._state = coordinator.data[PRINTER_PRINT_VOLUME]
        self.set_id("print_volume")
        self.set_name("Print Volume")
        
    @property
    def unit_of_measurement(self):
        return "pages"

    @property
    def icon(self):
        return "mdi:file-document-multiple-outline"
    
    @property
    def state(self):
        return self.coordinator.data[PRINTER_PRINT_VOLUME]

    @property
    def entity_category(self):
        return "diagnostic"
