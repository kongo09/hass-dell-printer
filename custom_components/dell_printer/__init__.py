"""The Dell printer component."""
from __future__ import annotations

from dell_printer_parser.printer_parser import DellPrinterParser

from .const import DOMAIN, PLATFORMS

from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST
from homeassistant.config_entries import ConfigEntry

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed


import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup a Dell printer from a config entry."""

     _LOGGER.debug(f"async_setup_entry: {entry}")

    # get the host address
    host = entry.data[CONF_HOST]

    # setup the parser
    session = async_get_clientsession(hass)
    printer = DellPrinterParser(session, host)

    # get a coordinator
    coordinator = DellDataUpdateCoordinator(hass, printer)
    await coordinator.async_config_entry_first_refresh()

    return True


async def async_unload_entry(hass: HomeAssistant, entry):
    await hass.data[DOMAIN][entry.entry_id].unload()
    for p in PLATFORMS:
        await hass.config_entries.async_forward_entry_unload(entry, p)
    hass.data[DOMAIN].pop(entry.entry_id)
    return True


async def async_setup(hass: HomeAssistant, config) -> bool:
    hass.data[DOMAIN] = dict()
    return True


class DellDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from Dell printer."""

    def __init__(
        self, hass: HomeAssistant, printer: DellPrinterParser
    ) -> None:
        """Initialize."""

        self.printer = DellPrinterParser(session, host)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL
        )

    async def _async_update_data(self) -> DictToObj:
        """Update data via library."""

        try:
            data = await self.brother.async_update()
        except (ConnectionError) as error:
            raise UpdateFailed(error) from error
        return data
