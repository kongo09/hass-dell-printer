"""The Dell printer component."""
from __future__ import annotations
from typing import Dict
from datetime import timedelta

from dell_printer_parser.printer_parser import DellPrinterParser

from .const import *

from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.config_entries import ConfigEntry

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup a Dell printer from a config entry."""

    _LOGGER.debug(f"async_setup_entry: {entry}")

    # get the host address
    host = entry.data[CONF_HOST]
    _LOGGER.debug(f"async_setup_entry host: {host}")


    # setup the parser
    update_interval = entry.data[CONF_SCAN_INTERVAL]
    _LOGGER.debug(f"async_setup_entry update_interval: {update_interval}")
    session = async_get_clientsession(hass)
    printer = DellPrinterParser(session, host)    
    _LOGGER.debug(f"async_setup_entry: DellPrinterParser {printer}")

    # setup a coordinator
    coordinator = DellDataUpdateCoordinator(hass, _LOGGER, printer, timedelta(seconds=update_interval))
    _LOGGER.debug(f"async_setup_entry: coordinator before first refresh DellPrinterParser {coordinator.printer}")
    await coordinator.async_config_entry_first_refresh()
    _LOGGER.debug(f"async_setup_entry: coordinator after first refresh DellPrinterParser {coordinator.printer}")
    _LOGGER.debug(f"async_setup_entry: coordinator model = {coordinator.printer.information.modelName}")
    
    # store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # setup sensors
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class DellDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Dell data from the printer."""

    def __init__(self, hass: HomeAssistant, _LOGGER, printer: DellPrinterParser, update_interval: timedelta) -> None:
        """Initialize."""

        _LOGGER.debug(f"coordinator __init__ with printer: {printer}")
        self.printer = printer
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)


    async def _async_update_data(self) -> Dict:
        """Update data via library."""

        _LOGGER.debug(f"coordinator _async_update_data called")
        _LOGGER.debug(f"coordinator printer: {self.printer}")

        try:
            """Ask the library to reload fresh data."""
            self.printer.load_data()
            _LOGGER.debug(f"coordinator load_data() called")
            _LOGGER.debug(f"coordinator model = {self.printer.information.modelName}")
        except (ConnectionError) as error:
            raise UpdateFailed(error) from error

        """Stick the data into a dictionary and return this for further usage."""
        data = {}

        data[MODEL_NAME] = self.printer.information.modelName
        data[DELL_SERVICE_TAG_NUMBER] = self.printer.information.dellServiceTagNumber
        data[ASSET_TAG_NUMBER] = self.printer.information.assetTagNumber
        data[PRINTER_SERIAL_NUMBER] = self.printer.information.printerSerialNumber
        data[MEMORY_CAPACITY] = self.printer.information.memoryCapacity
        data[PROCESSOR_SPEED] = self.printer.information.processorSpeed
        data[FIRMWARE_VERSION] = self.printer.information.firmwareVersion
        data[NETWORK_FIRMWARE_VERSION] = self.printer.information.networkFirmwareVersion
        data[CYAN_LEVEL] = self.printer.status.cyanLevel
        data[MAGENTA_LEVEL] = self.printer.status.magentaLevel
        data[YELLOW_LEVEL] = self.printer.status.yellowLevel
        data[BLACK_LEVEL] = self.printer.status.blackLevel
        data[MULTI_PURPOSE_FEEDER_STATUS] = self.printer.status.multiPurposeFeederStatus
        data[MULTI_PURPOSE_FEEDER_CAPACITY] = self.printer.status.multiPurposeFeederCapacity
        data[MULTI_PURPOSE_FEEDER_SIZE] = self.printer.status.multiPurposeFeederSize
        data[OUTPUT_TRAY_STATUS] = self.printer.status.outputTrayStatus
        data[OUTPUT_TRAY_CAPACITY] = self.printer.status.outputTrayCapacity
        data[REAR_COVER_STATUS] = self.printer.status.rearCoverStatus
        data[ADF_COVER_STATUS] = self.printer.status.adfCoverStatus
        data[PRINTER_TYPE] = self.printer.status.printerType
        data[PRINTING_SPEED] = self.printer.status.printingSpeed
        data[PRINTER_PAGE_COUNT] = self.printer.printVolume.printerPageCount
        data[PAPER_USED_LETTER] = self.printer.printVolume.paperUsedLetter
        data[PAPER_USED_A5] = self.printer.printVolume.paperUsedA5
        data[PAPER_USED_B5] = self.printer.printVolume.paperUsedB5
        data[PAPER_USED_A4] = self.printer.printVolume.paperUsedA4
        data[PAPER_USED_EXECUTIVE] = self.printer.printVolume.paperUsedExecutive
        data[PAPER_USED_FOLIO] = self.printer.printVolume.paperUsedFolio
        data[PAPER_USED_LEGAL] = self.printer.printVolume.paperUsedLegal
        data[PAPER_USED_ENVELOPE] = self.printer.printVolume.paperUsedEnvelope
        data[PAPER_USED_MONARCH] = self.printer.printVolume.paperUsedMonarch
        data[PAPER_USED_DL] = self.printer.printVolume.paperUsedDL
        data[PAPER_USED_C5] = self.printer.printVolume.paperUsedC5
        data[PAPER_USED_OTHERS] = self.printer.printVolume.paperUsedOthers

        _LOGGER.debug(f"coordinator retrieved data: {data}")

        return data