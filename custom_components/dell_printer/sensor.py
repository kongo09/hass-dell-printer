from typing import Callable, Any, Dict
from custom_components.dell_printer import DellDataUpdateCoordinator
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.config_entries import ConfigEntry

import logging

from .const import ADF_COVER_STATUS, DOMAIN, FIRMWARE_VERSION, MODEL_NAME, OUTPUT_TRAY_CAPACITY, OUTPUT_TRAY_STATUS, PRINTER_PAGE_COUNT, PRINTER_SERIAL_NUMBER, REAR_COVER_STATUS

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
    entities.append(OutputTrayStatus(coordinator))
    
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
        self.attrs = {paper: used for paper, used in self.coordinator.data.items() if paper.startswith("paper_")}
        _LOGGER.debug(f"extra_state_attributes: {self.attrs}")
        return self.attrs


class Status(DellPrinterEntity, BinarySensorEntity):
    """Representation of a cover sensor."""

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        super().__init__(coordinator)
        self._attr_entity_category = "diagnostic"
        self._attr_device_class = "opening"

    def init_name(self, name: str) -> None:
        self.lower_name = name.lower().replace(" ", "_")
        self._id = DOMAIN + "_" + self.lower_name
        self._attr_name = name

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


class RearCoverStatus(Status, BinarySensorEntity):
    """Representation of a rear cover sensor."""

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        super().__init__(coordinator)
        self.init_name("Rear Cover")
        
    @property
    def is_on(self) -> bool:
        return self.coordinator.data[REAR_COVER_STATUS] == "Open"

    @property
    def state(self) -> str:
        return self.coordinator.data[REAR_COVER_STATUS]


class AdfCoverStatus(Status, BinarySensorEntity):
    """Representation of a ADF sensor."""

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        super().__init__(coordinator)
        self.init_name("ADF Cover")
        
    @property
    def is_on(self) -> bool:
        return self.coordinator.data[ADF_COVER_STATUS] == "Open"

    @property
    def state(self) -> str:
        return self.coordinator.data[ADF_COVER_STATUS]


class OutputTrayStatus(Status, BinarySensorEntity):
    """Representation of an output tray sensor."""

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        super().__init__(coordinator)
        self.init_name("Output Tray")
        
    @property
    def is_on(self) -> bool:
        return self.coordinator.data[OUTPUT_TRAY_STATUS] != "OK"

    @property
    def state(self) -> str:
        return self.coordinator.data[OUTPUT_TRAY_STATUS]

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        self.attrs = {OUTPUT_TRAY_CAPACITY: self.coordinator.data[OUTPUT_TRAY_CAPACITY]}
        return self.attrs

