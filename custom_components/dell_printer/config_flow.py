from homeassistant import config_entries, exceptions

from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.network import get_url

from typing import Any, Dict, Optional
from .dell import DellInterface

import logging
import voluptuous as vol

from .const import DEFAULT_NAME, DOMAIN, DEFAULT_PORT, POLLING_INTERVAL

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT): cv.string,
    },
    extra=vol.PREVENT_EXTRA,
)

class DellPrinterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    def _get_hass_url(self, hass):
        try:
            return get_url(hass)
        except Exception as err:
            _LOGGER.exception(f"Error getting HASS url: {err}")
            return ""

    async def async_step_user(self, user_input=None):
        _LOGGER.debug("async_step_user called")
        _LOGGER.debug(f"Input: {user_input}")

        errors = {}

        # todo: there could potentially be more than one printer
        if self._async_current_entries():
            # Config entry already exists, only one allowed.
            _LOGGER.debug("async_abort will be called")
            return self.async_abort(reason="single_instance_allowed")

        # user input was provided, so check and save it
        if user_input is not None:
            
            # do some checks first
            if not user_input.get("address"):
                errors["address"] = "no_printer_url"
            if not user_input.get("port"):
                errors["port"] = "no_printer_port"

            # if there are no errors, we can create a configuration entry
            if not errors:
                _LOGGER.debug("async_create_entry will be called")
                return self.async_create_entry(
                    title=user_input.get("name") or DEFAULT_NAME,
                    data=user_input
                )

        # no input or error so far
        if user_input is None:
            _LOGGER.debug("so far no user input")
            hass_url = self._get_hass_url(self.hass)
            user_input = {
                "hass_url": hass_url
            }
        
        # what to ask the user
        schema = vol.Schema({
            vol.Optional("name", default=user_input.get("name", DEFAULT_NAME)): cv.string,
            vol.Required("address", default=user_input.get("address", "")): cv.string,
            vol.Required("port", default=user_input.get("port", DEFAULT_PORT)): vol.All(
                cv.positive_int,
                vol.Range(min=0, max=65535)
            ),
            vol.Optional("hass_url", default=user_input.get("hass_url", "")): cv.string,
            vol.Required("update_seconds", default=user_input.get("update_seconds", POLLING_INTERVAL)): vol.All(
                cv.positive_int,
                vol.Range(min=10, max=600)
            ),
        })

        # show the form to the user
        _LOGGER.debug("async_show_form will be called")
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_zeroconf(self, discovery_info: Optional[Dict[str, Any]]=None):

        errors = {}

        """Handle zeroconf discovery."""
        _LOGGER.debug("async_step_zeroconf called")
        _LOGGER.debug(f"Input: {discovery_info}")

        # Hostname is format: DELLDCCFBB.local.
        _LOGGER.debug(f"Discovered hostname: {discovery_info.hostname}")
        _LOGGER.debug(f"Discovered host: {discovery_info.host}")
        _LOGGER.debug(f"Discovered port: {discovery_info.port}")
        _LOGGER.debug(f"Discovered type: {discovery_info.type}")
        _LOGGER.debug(f"Discovered name: {discovery_info.name}")

        return self.async_abort(reason="zeroconf not finished yet")