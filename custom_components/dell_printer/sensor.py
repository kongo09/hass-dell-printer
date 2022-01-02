from typing import Callable, Optional
from custom_components.dell_printer import DellDataUpdateCoordinator
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType, HomeAssistantType
from homeassistant.config_entries import ConfigEntry

import logging

from .const import DEFAULT_NAME, DOMAIN, FIRMWARE_VERSION, MODEL_NAME, PRINTER_PAGE_COUNT, PRINTER_SERIAL_NUMBER

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry, async_add_entities: Callable):
    """Setup sensor entity."""

    _LOGGER.debug(f"async_setup_entry called")

    entities = []
    coordinator = hass.data[DOMAIN][entry.entry_id]

    _LOGGER.debug(f"async_setup_entry in sensor: appending entity")
    entities.append(PrintVolume(coordinator))
    
    async_add_entities(entities, update_before_add=True)
    return True


class DellPrinterEntity(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        _LOGGER.debug(f"DellPrinterEntity __init__ before super")
        super().__init__(coordinator)
        _LOGGER.debug(f"DellPrinterEntity __init__ after super")
        self._serialNumber = coordinator.data[PRINTER_SERIAL_NUMBER]
        self._modelName = coordinator.data[MODEL_NAME]
        self._firmware = coordinator.data[FIRMWARE_VERSION]
        self._name = self._serialNumber
        self._available = True

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self._serialNumber)
            },
            "name": self._name,
            "model": self._modelName,
            "manufacturer": "Dell",
            "sw_version": self._firmware,
        }

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available


class PrintVolume(DellPrinterEntity):
    """Representation of a sensor."""

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        _LOGGER.debug(f"PrintVolume __init__ before super")
        super().__init__(coordinator)
        _LOGGER.debug(f"PrintVolume __init__ after super")
        self.attrs = {}
        # self._state = coordinator.data[PRINTER_PRINT_VOLUME]
        self._id = "print_volume"
        self._attr_name = "Print Volume"
        self._attr_icon = "mdi:file-document-multiple-outline"
        self._attr_native_unit_of_measurement = "pages"
        self._attr_state_class = "measurement"
        self._attr_entity_category = "diagnostic"
        
    @property
    def state(self):
        pageCount = self.coordinator.data[PRINTER_PAGE_COUNT]
        _LOGGER.debug(f"state: {pageCount}")
        return pageCount

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._serialNumber + "_print_volume"