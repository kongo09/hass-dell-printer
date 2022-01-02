"""The Dell Printer component."""
from homeassistant import config_entries, exceptions
from homeassistant.components import zeroconf
from homeassistant.data_entry_flow import FlowResult

from homeassistant.const import CONF_HOST, CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from dell_printer_parser.printer_parser import DellPrinterParser

from aiohttp.client_exceptions import ClientConnectorError

from typing import Any, Dict, Optional
import ipaddress
import re

import logging
import voluptuous as vol

from .const import DEFAULT_NAME, DOMAIN, POLLING_INTERVAL

_LOGGER = logging.getLogger(__name__)



def host_valid(host: str) -> bool:
    """Return True if hostname or IP address is valid."""
    try:
        if ipaddress.ip_address(host).version in [4, 6]:
            return True
    except ValueError:
        pass
    disallowed = re.compile(r"[^a-zA-Z\d\-]")
    return all(x and not disallowed.search(x) for x in host.split("."))


class UnsupportedModel(Exception):
    """Raised when no model, serial no, firmware data."""


class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate that hostname/IP address is invalid."""


class DellPrinterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow for DELL printers."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize."""
        self.printer: DellPrinterParser = None
        self.host: str = None


    def _get_schema(self, user_input):
        """Provide schema for user input."""
        schema = vol.Schema({
            vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
            vol.Required(CONF_HOST, default=""): cv.string,
            vol.Required(CONF_SCAN_INTERVAL, default=POLLING_INTERVAL): vol.All(
                cv.positive_int,
                vol.Range(min=10, max=600)
            ),
        })
        return schema


    async def async_step_user(self, user_input: dict[str, Any] = None) -> FlowResult:
        """Handle initial step of user config flow."""

        errors = {}

        # user input was provided, so check and save it
        if user_input is not None:
            try:
                # first some sanitycheck on the host input
                if not host_valid(user_input[CONF_HOST]):
                    raise InvalidHost()

                # now let's try and see if we can connect to a printer
                session = async_get_clientsession(self.hass)
                printer = DellPrinterParser(session, user_input[CONF_HOST])

                # try to load some data
                await printer.load_data()

                # use the serial number as unique id
                unique_id = printer.information.printerSerialNumber

                # check if we got something
                if not unique_id:
                    raise UnsupportedModel()

                # set the unique id for the entry, abort if it already exists
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                # compile a name from model and serial
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME) or printer.information.modelName,
                    data=user_input
                )

            except InvalidHost:
                errors[CONF_HOST] = "wrong host"
            except ConnectionError:
                errors[CONF_HOST] = "cannot connect"
            except ClientConnectorError:
                errors[CONF_HOST] = "cannot connect"
            except UnsupportedModel:
                errors['base'] = "printer model not supported"

        # no user_input so far
        # what to ask the user
        schema = self._get_schema(user_input)

        # show the form to the user
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)


    async def async_step_zeroconf(self, discovery_info: zeroconf.ZeroconfServiceInfo = None
        # discovery_info: Optional[Dict[str, Any]] = None
    ):
        """Handle zeroconf flow."""

        errors = {}

        # extract some data from zeroconf
        self.host = discovery_info.host
        _LOGGER.debug(f"discovered: {discovery_info}")

        # if the hostname already exists, we can stop
        self._async_abort_entries_match({CONF_HOST: self.host})

        # now let's try and see if we can connect to a printer
        session = async_get_clientsession(self.hass)
        self.printer = DellPrinterParser(session, self.host)

        # try to load some data
        try:
            await self.printer.load_data()
        except ConnectionError:
            self.async_abort(reason="cannot_connect")
        except ClientConnectorError:
            self.async_abort(reason="cannot_connect")

        # use the serial number as unique id
        unique_id = self.printer.information.printerSerialNumber

        # check if we got something
        if not unique_id:
            self.async_abort(reason="unsupported_model")

        # set the unique id for the entry, abort if it already exists
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        # store the data for the next step to get confirmation
        self.context.update({
            "title_placeholders": {
                CONF_NAME: self.printer.information.modelName,
                CONF_SCAN_INTERVAL: POLLING_INTERVAL,
            }
        })

        # show the form to the user
        return await self.async_step_zeroconf_confirm()


    async def async_step_zeroconf_confirm(
        self,
        user_input: dict[str, Any] = None
    ) -> FlowResult:
        """Confirm the zeroconf discovered data."""

        # user input was provided, so check and save it
        if user_input is not None:
            
            return self.async_create_entry(
                title=self.printer.information.modelName,
                data={
                    CONF_NAME: user_input[CONF_NAME],
                    CONF_HOST: self.host,
                    CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL]
                }
            )

        # show the form to the user
        name = self.printer.information.modelName
        return self.async_show_form(
            step_id="zeroconf_confirm",
            data_schema=vol.Schema({
                vol.Optional(CONF_NAME, default=name): cv.string,
                vol.Required(CONF_SCAN_INTERVAL, default=POLLING_INTERVAL): vol.All(
                    cv.positive_int,
                    vol.Range(min=10, max=600)),
            }),
            description_placeholders={
                CONF_HOST: self.host
            }
        )
