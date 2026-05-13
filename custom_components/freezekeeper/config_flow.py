from __future__ import annotations

import uuid
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_HA_URL,
    CONF_LABEL_TYPE,
    CONF_PRINT_1D_BARCODE,
    CONF_PRINTER_URL,
    DEFAULT_LABEL_TYPE,
    DEFAULT_PRINT_1D_BARCODE,
    DOMAIN,
)

LABEL_TYPES = {"62": "62 mm – DK-22205 (Endlos)", "62red": "62 mm – DK-22251 (Endlos, 2-farbig)"}

_SCHEMA = vol.Schema({
    vol.Required(CONF_PRINTER_URL): str,
    vol.Optional(CONF_LABEL_TYPE, default=DEFAULT_LABEL_TYPE): vol.In(LABEL_TYPES),
    vol.Optional(CONF_PRINT_1D_BARCODE, default=DEFAULT_PRINT_1D_BARCODE): bool,
    vol.Optional(CONF_HA_URL, default=""): str,
})


class FreezeKeeperConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> Any:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if user_input is not None:
            return self.async_create_entry(
                title="FreezeKeeper",
                data={**user_input, "webhook_id": uuid.uuid4().hex},
            )
        return self.async_show_form(step_id="user", data_schema=_SCHEMA)

    async def async_step_reconfigure(self, user_input: dict | None = None) -> Any:
        entry = self._get_reconfigure_entry()
        if user_input is not None:
            return self.async_update_reload_and_abort(entry, data_updates=user_input)
        current = {**entry.data, **entry.options}
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(_SCHEMA, current),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> "FreezeKeeperOptionsFlow":
        return FreezeKeeperOptionsFlow()


class FreezeKeeperOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input: dict | None = None) -> Any:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        current = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(_SCHEMA, current),
        )
