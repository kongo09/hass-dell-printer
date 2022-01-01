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
        self._id = "print_volume"
        self._name = "Print Volume"
        self._icon = "mdi:file-document-multiple-outline"
        self._native_unit_of_measurement = "pages"
        self._state_class = "measurement"
        self._entity_category = "diagnostic"
        
    @property
    def native_value(self):
        return self.coordinator.data[PRINTER_PRINT_VOLUME]
