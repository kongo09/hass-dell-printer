from typing import Callable
from custom_components.dell_printer import DellDataUpdateCoordinator
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType, HomeAssistantType
from homeassistant.config_entries import ConfigEntry

import logging

from .const import DEFAULT_NAME, DOMAIN, FIRMWARE_VERSION, MODEL_NAME, PRINTER_PAGE_COUNT, PRINTER_SERIAL_NUMBER

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass: HomeAssistantType, config: ConfigType, async_add_entities: Callable, discovery_info: Optional[DiscoverInfoType] = None) -> None:
    """Setup sensor platform."""

    _LOGGER.debug(f"async_setup_platform called")
    _LOGGER.debug(f"config: {config}")




async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry, async_add_entities: Callable):
    """Setup sensor entity."""

    _LOGGER.debug(f"async_setup_entry called")

    entities = []
    coordinator = hass.data[DOMAIN][entry.entry_id]

    _LOGGER.debug(f"async_setup_entry in sensor: appending entity")
    entities.append(PrintVolume(coordinator))
    
    async_add_entities(entities, True)
    return True


class DellPrinterEntity(CoordinatorEntity):

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        super().__init__(coordinator)
        self._serialNumber = coordinator.data[PRINTER_SERIAL_NUMBER]
        self._modelName = coordinator.data[MODEL_NAME]
        self._firmware = coordinator.data[FIRMWARE_VERSION]
        self._name = DEFAULT_NAME

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self._serialNumber)
            },
            "name": self._name,
            "manufacturer": "Dell",
            "model": self._modelName,
            "sw_version": self._firmware,
        }


class PrintVolume(DellPrinterEntity):
    """Representation of a sensor."""

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        super().__init__(coordinator)
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
