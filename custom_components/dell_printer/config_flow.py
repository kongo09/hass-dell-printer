from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.network import get_url
from .constants import DOMAIN
from .dell import DellInterface

import logging
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)


class DellPrinterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_reauth(self, user_input):
        return await self.async_step_user(user_input)

    async def find_dell_printers(self, config: dict):
        nuki = DellInterface(
            self.hass,
            bridge=config["address"],
            token=config["token"]
        )
        title = None
        if config["token"]:
            try:
                response = await nuki.bridge_list()
                _LOGGER.debug(f"bridge devices: {response}")
                title = response[0]["name"]
            except Exception as err:
                _LOGGER.exception(
                    f"Failed to get list of devices from bridge: {err}")
                return title, "invalid_bridge_token"
        return title, None

    def _get_hass_url(self, hass):
        try:
            return get_url(hass)
        except Exception as err:
            _LOGGER.exception(f"Error getting HASS url: {err}")
            return ""

    async def async_step_user(self, user_input):
        errors = None
        _LOGGER.debug(f"Input: {user_input}")
        if user_input is None:
            nuki = DellInterface(self.hass)
            bridge_address = await nuki.discover_bridge()
            hass_url = self._get_hass_url(self.hass)
            user_input = {
                "address": bridge_address,
                "hass_url": hass_url
            }
        elif not user_input.get("token"):
            errors = dict(base="no_token")
        elif user_input.get("token") and not user_input.get("address"):
            errors = dict(base="no_bridge_url")
        elif user_input.get("token"):
            title, err = await self.find_dell_printers(user_input)
            if not err:
                return self.async_create_entry(
                    title=user_input.get("name") or title,
                    data=user_input
                )
            errors = dict(base=err)
        schema = vol.Schema({
            vol.Required("address", default=user_input.get("address", "")): cv.string,
            vol.Optional("hass_url", default=user_input.get("hass_url", "")): cv.string,
            vol.Required("token", default=user_input.get("token", "")): cv.string,
            vol.Optional("name", default=user_input.get("name", "")): cv.string,
            vol.Required("update_seconds", default=user_input.get("update_seconds", 30)): vol.All(
                cv.positive_int,
                vol.Range(min=10, max=600)
            ),
        })
        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

class OptionsFlowHandler(config_entries.OptionsFlow):

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        data = self.config_entry.as_dict()["data"]
        _LOGGER.debug(f"OptionsFlowHandler: {data} {self.config_entry}")
        schema = vol.Schema({
            vol.Required("hass_url", default=data.get("hass_url")): cv.string,
            vol.Required("token", default=data.get("token")): cv.string,
        })
        return self.async_show_form(
            step_id="options", data_schema=schema
        )
