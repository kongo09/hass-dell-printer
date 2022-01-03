from typing import Callable, Any, Dict
from custom_components.dell_printer import DellDataUpdateCoordinator
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.config_entries import ConfigEntry

import logging

from .const import ADF_COVER_STATUS, ASSET_TAG_NUMBER, BLACK_LEVEL, CYAN_LEVEL, DELL_SERVICE_TAG_NUMBER, DOMAIN, FIRMWARE_VERSION, MAGENTA_LEVEL, MEMORY_CAPACITY, MODEL_NAME, MULTI_PURPOSE_FEEDER_CAPACITY, MULTI_PURPOSE_FEEDER_SIZE, MULTI_PURPOSE_FEEDER_STATUS, NETWORK_FIRMWARE_VERSION, OUTPUT_TRAY_CAPACITY, OUTPUT_TRAY_STATUS, PRINTER_PAGE_COUNT, PRINTER_SERIAL_NUMBER, PRINTER_TYPE, PRINTING_SPEED, PROCESSOR_SPEED, REAR_COVER_STATUS, YELLOW_LEVEL

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
    entities.append(PaperTrayStatus(coordinator))
    entities.append(CyanStatus(coordinator))
    entities.append(MagentaStatus(coordinator))
    entities.append(YellowStatus(coordinator))
    entities.append(BlackStatus(coordinator))
    
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


class PrinterInfo(DellPrinterEntity, BinarySensorEntity):
    """Representation of the printer."""

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        super().__init__(coordinator)
        # self._id = DOMAIN + "_info"
        self._attr_unique_id = self._serialNumber + "_info"
        self._attr_name = self._modelName
        self._attr_state_class = "measurement"
        self._attr_entity_category = "diagnostic"

    @property
    def is_on(self) -> bool:
        return False

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
            PRINTING_SPEED: self.coordinator.data[PRINTING_SPEED]
        }


class PrintVolume(DellPrinterEntity, SensorEntity):
    """Representation of a sensor."""

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        super().__init__(coordinator)
        self._id = DOMAIN + "_print_volume"
        self._attr_unique_id = self._serialNumber + "_print_volume"
        self._attr_name = "Print Volume"
        self._attr_icon = "mdi:tray-full"
        self._attr_native_unit_of_measurement = "pages"
        self._attr_state_class = "measurement"
        self._attr_entity_category = "diagnostic"
        
    @property
    def state(self) -> int:
        return self.coordinator.data[PRINTER_PAGE_COUNT]

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return {
            paper.removeprefix("paper_used_"): used
            for paper, used in self.coordinator.data.items()
            if paper.startswith("paper_")
        }


class TonerStatus(DellPrinterEntity, SensorEntity):
    """Representation of a toner sensor."""

    def __init__(self, coordinator: DellDataUpdateCoordinator, name: str):
        super().__init__(coordinator)
        self._attr_entity_category = "diagnostic"
        self._attr_native_unit_of_measurement = "%"
        self._attr_state_class = "measurement"
        self.lower_name = name.lower().replace(" ", "_")
        self._id = DOMAIN + "_" + self.lower_name
        self._attr_unique_id = self._serialNumber + "_" + self.lower_name          
        self._attr_name = name

    @property
    def icon(self) -> str:
        """Return icon depending on state."""
        if self.state >= 10:
            return "mdi:water"
        elif self.state >= 2:
            return "mdi:water-alert"
        else:
            return "mdi:water-off"


class CyanStatus(TonerStatus):
    """Representation of cyan toner."""

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        super().__init__(coordinator, "Cyan")

    @property
    def state(self) -> int:
        return self.coordinator.data[CYAN_LEVEL]


class MagentaStatus(TonerStatus):
    """Representation of magenta toner."""

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        super().__init__(coordinator, "Magenta")

    @property
    def state(self) -> int:
        return self.coordinator.data[MAGENTA_LEVEL]


class YellowStatus(TonerStatus):
    """Representation of yellow toner."""

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        super().__init__(coordinator, "Yellow")

    @property
    def state(self) -> int:
        return self.coordinator.data[YELLOW_LEVEL]


class BlackStatus(TonerStatus):
    """Representation of black toner."""

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        super().__init__(coordinator, "Black")

    @property
    def state(self) -> int:
        return self.coordinator.data[BLACK_LEVEL]


class Status(DellPrinterEntity, BinarySensorEntity):
    """Representation of a cover sensor."""

    def __init__(self, coordinator: DellDataUpdateCoordinator, name: str):
        super().__init__(coordinator)
        self._attr_entity_category = "diagnostic"
        self._attr_device_class = "opening"
        self.lower_name = name.lower().replace(" ", "_")
        self._id = DOMAIN + "_" + self.lower_name
        self._attr_unique_id = self._serialNumber + "_" + self.lower_name
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
