from typing import Callable, Any, Dict
from custom_components.dell_printer import DellDataUpdateCoordinator, DellPrinterEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.config_entries import ConfigEntry
from homeassistant.util import slugify

import logging

from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry, async_add_entities: Callable):
    """Setup binary sensor entity."""

    _LOGGER.debug(f"async_setup_entry called")

    entities = []
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities.append(RearCoverStatus(coordinator))
    entities.append(AdfCoverStatus(coordinator))
    entities.append(OutputTrayStatus(coordinator))
    entities.append(PaperTrayStatus(coordinator))
    entities.append(PrinterInfo(coordinator))
    
    async_add_entities(entities, update_before_add=True)
    return True


class PrinterInfo(DellPrinterEntity, BinarySensorEntity):
    """Representation of the printer."""

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        super().__init__(coordinator)
        self._attr_unique_id = self._serialNumber + "_info"
        self._attr_name = self._modelName
        self.entity_id = "binary_sensor." + slugify(DEFAULT_NAME + " " + self._modelName)
        self._attr_state_class = "measurement"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def is_on(self) -> bool:
        return "ready" not in self.coordinator.data[EVENT_DETAILS].lower()

    @property
    def state(self) -> str:
        if self.is_on:
            return "Error"
        else:
            return "Ready"

    @property
    def icon(self) -> str:
        """Return icon depending on state."""
        if self.is_on:
            return "mdi:printer-alert"
        else:
            return "mdi:printer"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return {
            DELL_SERVICE_TAG_NUMBER: self.coordinator.data[DELL_SERVICE_TAG_NUMBER],
            ASSET_TAG_NUMBER: self.coordinator.data[ASSET_TAG_NUMBER],
            PRINTER_SERIAL_NUMBER: self.coordinator.data[PRINTER_SERIAL_NUMBER],
            MEMORY_CAPACITY: self.coordinator.data[MEMORY_CAPACITY],
            PROCESSOR_SPEED: self.coordinator.data[PROCESSOR_SPEED],
            FIRMWARE_VERSION: self.coordinator.data[FIRMWARE_VERSION],
            NETWORK_FIRMWARE_VERSION: self.coordinator.data[NETWORK_FIRMWARE_VERSION],
            PRINTER_TYPE: self.coordinator.data[PRINTER_TYPE],
            PRINTING_SPEED: self.coordinator.data[PRINTING_SPEED],
            EVENT_LOCATION: self.coordinator.data[EVENT_LOCATION],
            EVENT_DETAILS: self.coordinator.data[EVENT_DETAILS]
        }


class Status(DellPrinterEntity, BinarySensorEntity):
    """Representation of a cover sensor."""

    def __init__(self, coordinator: DellDataUpdateCoordinator, name: str):
        super().__init__(coordinator)
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_class = "opening"
        self.lower_name = name.lower().replace(" ", "_")
        self._attr_unique_id = self._serialNumber + "_" + self.lower_name
        self.entity_id = "binary_sensor." + slugify(DEFAULT_NAME + " " + name)
        self._attr_name = name

    @property
    def icon(self) -> str:
        """Return icon depending on state."""
        if self.is_on:
            return "mdi:tray-alert"
        else:
            return "mdi:tray"


class RearCoverStatus(Status):
    """Representation of a rear cover sensor."""

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        super().__init__(coordinator, "Rear Cover")
        
    @property
    def is_on(self) -> bool:
        return self.coordinator.data[REAR_COVER_STATUS] == "Open"

    @property
    def state(self) -> str:
        return self.coordinator.data[REAR_COVER_STATUS]


class AdfCoverStatus(Status):
    """Representation of a ADF sensor."""

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        super().__init__(coordinator, "ADF Cover")
        
    @property
    def is_on(self) -> bool:
        return self.coordinator.data[ADF_COVER_STATUS] == "Open"

    @property
    def state(self) -> str:
        return self.coordinator.data[ADF_COVER_STATUS]


class OutputTrayStatus(Status):
    """Representation of an output tray sensor."""

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        super().__init__(coordinator, "Output Tray")
        
    @property
    def is_on(self) -> bool:
        return self.coordinator.data[OUTPUT_TRAY_STATUS] != "OK"

    @property
    def state(self) -> str:
        return self.coordinator.data[OUTPUT_TRAY_STATUS]

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        self.attrs = {
            "capacity": self.coordinator.data[OUTPUT_TRAY_CAPACITY]
        }
        return self.attrs
    
    @property
    def icon(self) -> str:
        """Return icon depending on state."""
        if self.is_on:
            return "mdi:tray-alert"
        else:
            return "mdi:tray-arrow-up"


class PaperTrayStatus(Status):
    """Representation of an output tray sensor."""

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        super().__init__(coordinator, "Multi Purpose Feeder")
        
    @property
    def is_on(self) -> bool:
        return self.coordinator.data[MULTI_PURPOSE_FEEDER_STATUS] != "Ready"

    @property
    def state(self) -> str:
        return self.coordinator.data[MULTI_PURPOSE_FEEDER_STATUS]

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        self.attrs = {
            "capacity": self.coordinator.data[MULTI_PURPOSE_FEEDER_CAPACITY],
            "size": self.coordinator.data[MULTI_PURPOSE_FEEDER_SIZE]
        }
        return self.attrs

    @property
    def icon(self) -> str:
        """Return icon depending on state."""
        if self.is_on:
            return "mdi:tray-alert"
        else:
            return "mdi:tray-arrow-down"
