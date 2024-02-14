"""Config flow for GigaChain integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
import types
from types import MappingProxyType
from homeassistant.helpers import selector
from homeassistant.helpers.selector import (
    TemplateSelector
)
import logging

LOGGER = logging.getLogger(__name__)

from .const import (
    DOMAIN,
    CONF_ENGINE,
    CONF_API_KEY,
    CONF_FOLDER_ID,
    CONF_CHAT_MODEL,
    CONF_TEMPERATURE,
    CONF_ENGINE_OPTIONS,
    CONF_PROMPT,
    CONF_MAX_TKNS,
    DEFAULT_CONF_TEMPERATURE,
    DEFAULT_CONF_MAX_TKNS,
    DEFAULT_CHAT_MODEL,
    DEFAULT_PROMPT,
    UNIQUE_ID,
)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ENGINE): selector.SelectSelector(
            selector.SelectSelectorConfig(options=CONF_ENGINE_OPTIONS),
        ),
    }
)

STEP_GIGACHAT_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): str
    }
)
STEP_YANDEXGPT_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): str,
        vol.Required(CONF_FOLDER_ID): str
    }
)
STEP_OPENAI_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): str
    }
)

ENGINE_SCHEMA = {
    "gigachat": STEP_GIGACHAT_SCHEMA,
    "yandexgpt": STEP_YANDEXGPT_SCHEMA,
    "openai": STEP_OPENAI_SCHEMA
}

DEFAULT_OPTIONS = types.MappingProxyType(
    {
        CONF_PROMPT: DEFAULT_PROMPT,
        CONF_CHAT_MODEL: DEFAULT_CHAT_MODEL,
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GigaChain."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(step_id="user",
                                        data_schema=STEP_USER_SCHEMA)

        engine = user_input[CONF_ENGINE]
        unique_id = UNIQUE_ID[engine]
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()
        return self.async_show_form(
            step_id=engine, data_schema=ENGINE_SCHEMA[engine]
        )

    async def async_step_gigachat(
        self, user_input: dict[str, Any] | None = None) -> FlowResult:
        return await self.common_model_async_step("gigachat", user_input)

    async def async_step_yandexgpt(
        self, user_input: dict[str, Any] | None = None) -> FlowResult:
        return await self.common_model_async_step("yandexgpt", user_input)

    async def async_step_openai(self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        return await self.common_model_async_step("openai", user_input)

    async def common_model_async_step(self, engine, user_input):
        if user_input is None:
            return self.async_show_form(
                step_id=engine, data_schema=ENGINE_SCHEMA[engine]
            )
        user_input[CONF_ENGINE] = engine
        unique_id = UNIQUE_ID[engine]
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title=unique_id, data=user_input)

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlow(config_entry)

class OptionsFlow(config_entries.OptionsFlow):
    """GigaChain config flow options handler."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title=self.config_entry.unique_id, data=user_input)
        schema = common_config_option_schema(self.config_entry.options)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema),
        )

def common_config_option_schema(options: MappingProxyType[str, Any]) -> dict:
    """Return a schema for GigaChain completion options."""
    if not options:
        options = DEFAULT_OPTIONS
    return {
        vol.Optional(
            CONF_PROMPT,
            description={"suggested_value": options[CONF_PROMPT]},
            default=DEFAULT_PROMPT,
        ): TemplateSelector(),
        vol.Optional(
            CONF_CHAT_MODEL,
            description={
                # New key in HA 2023.4
                "suggested_value": options.get(CONF_CHAT_MODEL,
                                               DEFAULT_CHAT_MODEL)
            },
            default=DEFAULT_CHAT_MODEL,
        ): str,
        vol.Optional(
            CONF_TEMPERATURE,
            description={
                # New key in HA 2023.4
                "suggested_value": options.get(CONF_TEMPERATURE,
                                               DEFAULT_CONF_TEMPERATURE)
            },
            default=DEFAULT_CONF_TEMPERATURE,
        ): float,
        vol.Optional(
            CONF_MAX_TKNS,
            description={
                # New key in HA 2023.4
                "suggested_value": options.get(CONF_MAX_TKNS,
                                               DEFAULT_CONF_MAX_TKNS)
            },
            default=DEFAULT_CONF_MAX_TKNS,
        ): int,
    }
