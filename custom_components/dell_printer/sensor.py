from typing import Callable, Any, Dict
from custom_components.dell_printer import DellDataUpdateCoordinator
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType, HomeAssistantType
from homeassistant.config_entries import ConfigEntry

import logging

from .const import ATTR_PAPER_USED_B5, ATTR_PAPER_USED_LETTER, DEFAULT_NAME, DOMAIN, FIRMWARE_VERSION, MODEL_NAME, PAPER_USED_B5, PAPER_USED_LETTER, PRINTER_PAGE_COUNT, PRINTER_SERIAL_NUMBER, REAR_COVER_STATUS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry, async_add_entities: Callable):
    """Setup sensor entity."""

    _LOGGER.debug(f"async_setup_entry called")

    entities = []
    coordinator = hass.data[DOMAIN][entry.entry_id]

    _LOGGER.debug(f"async_setup_entry in sensor: appending entity")
    entities.append(PrintVolume(coordinator))
    entities.append(RearCoverStatus(coordinator))
    entities.append(AdfCoverStatus(coordinator))
    
    async_add_entities(entities, update_before_add=True)
    return True


class DellPrinterEntity(CoordinatorEntity):

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        super().__init__(coordinator)
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


class PrintVolume(DellPrinterEntity, SensorEntity):
    """Representation of a sensor."""

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        super().__init__(coordinator)
        self._id = DOMAIN + "_print_volume"
        self._attr_name = DOMAIN + " Print Volume"
        self._attr_icon = "mdi:file-document-multiple-outline"
        self._attr_native_unit_of_measurement = "pages"
        self._attr_state_class = "measurement"
        self._attr_entity_category = "diagnostic"
        self.attrs: Dict[str, Any]
        
    @property
    def state(self):
        pageCount = self.coordinator.data[PRINTER_PAGE_COUNT]
        _LOGGER.debug(f"state: {pageCount}")
        return pageCount

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._serialNumber + "_print_volume"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        _LOGGER.debug(f"extra_state_attributes called")
        _LOGGER.debug(f"raw: {self.coordinator.data.items()}")
        self.attrs = {paper: used for paper, used in self.coordinator.data.items() if paper.startswith("PAPER_")}
        _LOGGER.debug(f"extra_state_attributes: {self.attrs}")
        # self.attrs[PAPER_USED_LETTER] = self.coordinator.data[PAPER_USED_LETTER]
        # self.attrs[PAPER_USED_B5] = self.coordinator.data[PAPER_USED_B5]
        return self.attrs


class CoverStatus(DellPrinterEntity, BinarySensorEntity):
    """Representation of a cover sensor."""

    def __init__(self, coordinator: DellDataUpdateCoordinator, cover: str):
        super().__init__(coordinator)
        self.lower_name = cover.lower().replace(" ", "_")
        self._id = DOMAIN + "_" + self.lower_name
        self._attr_name = DOMAIN + " " + cover
        self._attr_entity_category = "diagnostic"
        self._attr_device_class = "opening"
        self.attrs: Dict[str, Any]

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._serialNumber + "_" + self.lower_name

    @property
    def icon(self) -> str:
        """Return icon depending on state."""
        if self.is_on:
            return "mdi:tray-alert"
        else:
            return "mdi:tray"


class RearCoverStatus(CoverStatus, BinarySensorEntity):
    """Representation of a sensor."""

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        super().__init__(coordinator, "Rear Cover")
        
    @property
    def is_on(self) -> bool:
        is_on = self.coordinator.data[REAR_COVER_STATUS] == "Closed"
        return is_on


class AdfCoverStatus(DellPrinterEntity, BinarySensorEntity):
    """Representation of a sensor."""

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        super().__init__(coordinator, "ADF Cover")
        
    @property
    def is_on(self) -> bool:
        is_on = self.coordinator.data[REAR_COVER_STATUS] == "Closed"
        return is_on

