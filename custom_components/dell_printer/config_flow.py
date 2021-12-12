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

class DellPrinterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    def _get_hass_url(self, hass):
        try:
            return get_url(hass)
        except Exception as err:
            _LOGGER.exception(f"Error getting HASS url: {err}")
            return ""

    def _get_schema(self, user_input):
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
        return schema

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
            
            _LOGGER.debug("checking if unique id is configured")
            self._abort_if_unique_id_configured()
            _LOGGER.debug("no, so async_create_entry will be called")
            return self.async_create_entry(
                title=user_input.get("name") or DEFAULT_NAME,
                data=user_input
            )

        # no input so far
        _LOGGER.debug("so far no user input")
        hass_url = self._get_hass_url(self.hass)
        user_input = {
            "hass_url": hass_url
        }
        
        # what to ask the user
        schema = self._get_schema(user_input)

        # show the form to the user
        _LOGGER.debug("async_show_form will be called")
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_zeroconf(self, discovery_info: Optional[Dict[str, Any]]=None):
        # process zeroconf data
        _LOGGER.debug("async_step_zeroconf called")

        errors = {}

        # extract some defaults from zeroconf
        hass_url = self._get_hass_url(self.hass)
        discovered = {
            "address": discovery_info.host,
            "port": discovery_info.port,
            "name": discovery_info.name.split('.')[0],
            "hass_url": hass_url,
            "update_seconds": POLLING_INTERVAL
        }
        _LOGGER.debug(f"Input: {discovered}")

        await self.async_set_unique_id(discovered.get("name"))

        # store the data for the next step
        self.context.update({
            "title.placeholders": {
                "address": discovered.get("address"),
                "port": discovered.get("port"),
                "name": discovered.get("name"),
                "hass_url": discovered.get("hass_url"),
                "update_seconds": discovered.get("update_seconds")
            }
        })

        # show the form to the user
        _LOGGER.debug("async_step_zeroconf_confirm will be called")
        return self.async_step_confirm()

    async def async_step_confirm(self, user_input: Dict[str, Any] = None):
        # confirm the zeroconf discovered data
        _LOGGER.debug("async_step_zeroconf_confirm called")

        errors = {} 

        # user input was provided, so check and save it
        if user_input is not None:
            
            _LOGGER.debug("checking if unique id is configured")
            self._abort_if_unique_id_configured()
            _LOGGER.debug("no, so async_create_entry will be called")
            return self.async_create_entry(
                title=user_input.get("name") or DEFAULT_NAME,
                data=user_input
            )

        # what to ask the user
        schema = self._get_schema(user_input)

        # show the form to the user
        _LOGGER.debug("async_show_form will be called")
        return self.async_show_form(step_id="confirm", data_schema=schema, errors=errors)
