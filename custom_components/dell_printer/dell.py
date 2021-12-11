from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.network import get_url
from homeassistant.components import webhook

import requests
import logging
import json
from datetime import timedelta
from urllib.parse import urlencode

from .constants import DOMAIN

_LOGGER = logging.getLogger(__name__)

BRIDGE_DISCOVERY_API = "https://api.nuki.io/discover/bridges"
BRIDGE_HOOK = "nuki_ng_bridge_hook"


class DellInterface:

    def __init__(
        self,
        hass,
        *,
        bridge: str = None,
        token: str = None,
    ):
        self.hass = hass
        self.bridge = bridge
        self.token = token

    async def async_json(self, cb):
        response = await self.hass.async_add_executor_job(lambda: cb(requests))
        if response.status_code >= 300:
            raise ConnectionError(f"Http response: {response.status_code}")
        if response.status_code > 200:
            return dict()
        json_resp = response.json()
        return json_resp

    async def discover_bridge(self) -> str:
        try:
            response = await self.async_json(
                lambda r: r.get(BRIDGE_DISCOVERY_API)
            )
            bridges = response.get("bridges", [])
            if len(bridges) > 0:
                return bridges[0]["ip"]
        except Exception as err:
            _LOGGER.exception(f"Failed to discover bridge:", err)
        return None

    def bridge_url(self, path: str, extra=None) -> str:
        extra_str = "&%s" % (urlencode(extra)) if extra else ""
        return f"http://{self.bridge}:8080{path}?token={self.token}{extra_str}"

    async def bridge_list(self):
        return await self.async_json(lambda r: r.get(self.bridge_url("/list")))

    async def bridge_info(self):
        return await self.async_json(lambda r: r.get(self.bridge_url("/info")))

    def web_url(self, path):
        return f"https://api.nuki.io{path}"

    def can_bridge(self):
        return True if self.token and self.bridge else False


class DellCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, entry, config: dict):
        self.entry = entry
        self.api = DellInterface(
            hass,
            bridge=config.get("address"),
            token=config.get("token")
        )
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_method=self._make_update_method(),
            update_interval=timedelta(seconds=config.get("update_seconds", 30))
        )

        hook_id = "%s_%s" % (BRIDGE_HOOK, entry.entry_id)

        url = config.get("hass_url", get_url(hass))
        self.bridge_hook = "{}{}".format(
            url, webhook.async_generate_path(hook_id))
        webhook.async_unregister(hass, hook_id)
        webhook.async_register(
            hass,
            DOMAIN,
            "bridge",
            hook_id,
            handler=self._make_bridge_hook_handler(),
        )

    def _add_update(self, dev_id: str, update):
        data = self.data
        if not data:
            return None
        previous = data.get("devices", {}).get(dev_id)
        if not previous:
            return None
        last_state = previous.get("lastKnownState", {})
        for key in last_state:
            if key in update:
                last_state[key] = update[key]
        previous["lastKnownState"] = last_state
        self.async_set_updated_data(data)

    async def _update(self):
        try:
            callbacks_list = None
            bridge_info = None
            info_mapping = dict()
            device_list = None
            if self.api.can_bridge():
                bridge_info = await self.api.bridge_info()
                for item in bridge_info.get("scanResults", []):
                    info_mapping[item.get("nukiId")] = item
                bridge_info["callbacks_list"] = callbacks_list
                device_list = await self.api.bridge_list()
            result = dict(devices={}, bridge_info=bridge_info)
            for item in device_list:
                dev_id = item["nukiId"]
                result["devices"][dev_id] = item
                result["devices"][dev_id]["bridge_info"] = info_mapping.get(
                    dev_id)
            _LOGGER.debug(f"_update: {json.dumps(result)}")
            return result
        except Exception as err:
            _LOGGER.exception(f"Failed to get latest data: {err}")
            raise UpdateFailed from err

    def _make_update_method(self):
        async def _update_data():
            return await self._update()
        return _update_data

    def _make_bridge_hook_handler(self):
        async def _hook_handler(hass, hook_id, request):
            body = await request.json()
            _LOGGER.debug(f"_hook_handler: {body}")
            self._add_update(body.get("nukiId"), body)

        return _hook_handler

    def device_data(self, dev_id: str):
        return self.data.get("devices", {}).get(dev_id, {})

    def info_data(self):
        return self.data.get("info", {})

    def device_supports(self, dev_id: str, feature: str) -> bool:
        return self.device_data(dev_id).get("lastKnownState", {}).get(feature) != None
