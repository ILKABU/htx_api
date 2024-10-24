"""Config flow for HTX API integration."""
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL

class HTXAPIConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HTX API."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=DEFAULT_SCAN_INTERVAL.total_seconds()
                    ): vol.All(vol.Coerce(int), vol.Range(min=1)),
                })
            )

        return self.async_create_entry(
            title="HTX API",
            data={
                CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
            },
        )
