from typing import Callable, Any, Dict
from custom_components.dell_printer import DellDataUpdateCoordinator, DellPrinterEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.config_entries import ConfigEntry
form homeassistant.util import slugify

import logging

from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry, async_add_entities: Callable):
    """Setup sensor entity."""

    _LOGGER.debug(f"async_setup_entry called")

    entities = []
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities.append(PrintVolume(coordinator))
    entities.append(CyanStatus(coordinator))
    entities.append(MagentaStatus(coordinator))
    entities.append(YellowStatus(coordinator))
    entities.append(BlackStatus(coordinator))
    
    async_add_entities(entities, update_before_add=True)
    return True


class PrintVolume(DellPrinterEntity, SensorEntity):
    """Representation of a sensor."""

    def __init__(self, coordinator: DellDataUpdateCoordinator):
        super().__init__(coordinator)
        self._attr_unique_id = self._serialNumber + "_print_volume"
        self.entity_id = "." + slugify(DEFAULT_NAME + " Print Volume")
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
        self._attr_unique_id = self._serialNumber + "_" + self.lower_name          
        self.entity_id = "." + slugify(DEFAULT_NAME + " " + name)
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