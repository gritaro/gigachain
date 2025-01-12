"""Config flow for GigaChain integration."""

from __future__ import annotations

import logging
import types
from types import MappingProxyType
from typing import Any

import voluptuous as vol
from gigachat.exceptions import ResponseError
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers.selector import (NumberSelector,
                                            NumberSelectorConfig,
                                            SelectSelectorMode,
                                            TemplateSelector)
from httpx import ConnectError

from .client_util import validate_client
from .const import (CONF_API_KEY, CONF_CHAT_MODEL, CONF_CHAT_MODEL_USER,
                    CONF_ENGINE, CONF_ENGINE_OPTIONS, CONF_FOLDER_ID,
                    CONF_MAX_TOKENS, CONF_PROFANITY, CONF_PROMPT,
                    CONF_SKIP_VALIDATION, CONF_TEMPERATURE, DEFAULT_CHAT_MODEL,
                    ENGINE_MODELS, DEFAULT_PROFANITY, DEFAULT_PROMPT,
                    DEFAULT_SKIP_VALIDATION, DEFAULT_TEMPERATURE, DOMAIN,
                    ID_GIGACHAT, ID_OPENAI, ID_YANDEX_GPT, UNIQUE_ID,
                    CONF_PROCESS_BUILTIN_SENTENCES, DEFAULT_PROCESS_BUILTIN_SENTENCES,
                    CONF_CHAT_HISTORY, DEFAULT_CHAT_HISTORY,
                    UNIQUE_ID_GIGACHAT, UNIQUE_ID_ANYSCALE, ID_ANYSCALE)

LOGGER = logging.getLogger(__name__)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ENGINE): selector.SelectSelector(
            selector.SelectSelectorConfig(options=CONF_ENGINE_OPTIONS),
        ),
    }
)
STEP_API_KEY_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): str,
        vol.Optional(
            CONF_SKIP_VALIDATION, default=DEFAULT_SKIP_VALIDATION
        ): bool,
    }
)
STEP_YANDEXGPT_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): str,
        vol.Required(CONF_FOLDER_ID): str,
        vol.Optional(
            CONF_SKIP_VALIDATION, default=DEFAULT_SKIP_VALIDATION
        ): bool,
    }
)

ENGINE_SCHEMA = {
    ID_GIGACHAT: STEP_API_KEY_SCHEMA,
    ID_YANDEX_GPT: STEP_YANDEXGPT_SCHEMA,
    ID_OPENAI: STEP_API_KEY_SCHEMA,
    ID_ANYSCALE: STEP_API_KEY_SCHEMA,
}

DEFAULT_OPTIONS = types.MappingProxyType(
    {
        CONF_PROMPT: DEFAULT_PROMPT,
        CONF_CHAT_MODEL: DEFAULT_CHAT_MODEL,
        CONF_CHAT_MODEL_USER: DEFAULT_CHAT_MODEL,
        CONF_PROCESS_BUILTIN_SENTENCES: DEFAULT_PROCESS_BUILTIN_SENTENCES,
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
            return self.async_show_form(step_id="user", data_schema=STEP_USER_SCHEMA)

        engine = user_input[CONF_ENGINE]
        unique_id = UNIQUE_ID[engine]
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()
        return self.async_show_form(step_id=engine, data_schema=ENGINE_SCHEMA[engine])

    async def async_step_gigachat(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        return await self.common_model_async_step(ID_GIGACHAT, user_input)

    async def async_step_yandexgpt(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        return await self.common_model_async_step(ID_YANDEX_GPT, user_input)

    async def async_step_anyscale(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        return await self.common_model_async_step(ID_ANYSCALE, user_input)

    async def async_step_openai(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        return await self.common_model_async_step(ID_OPENAI, user_input)

    async def common_model_async_step(self, engine, user_input):
        if user_input is None:
            return self.async_show_form(
                step_id=engine, data_schema=ENGINE_SCHEMA[engine]
            )

        errors = {}
        user_input[CONF_ENGINE] = engine
        unique_id = UNIQUE_ID[engine]
        try:
            await validate_client(self.hass, user_input)
        except ConnectError:
            errors["base"] = "cannot_connect"
        except ResponseError:
            errors["base"] = "invalid_response"
        except Exception as inst:
            LOGGER.exception("Unexpected exception %s", type(inst))
            errors["base"] = "unknown"
        else:
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=unique_id, data=user_input)

        return self.async_show_form(
            step_id=engine, data_schema=ENGINE_SCHEMA[engine], errors=errors
        )

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
        errors = {}
        unique_id = self.config_entry.unique_id
        schema = common_config_option_schema(
            unique_id, self.config_entry.options
        )
        if user_input is not None:
            errors["base"] = "unsupported"
            if unique_id == UNIQUE_ID_ANYSCALE:
                return self.async_show_form(
                    step_id="init", data_schema=schema, errors=errors
                )
            model = user_input.get(CONF_CHAT_MODEL_USER)
            if model == " " or model == "" or model is None:
                model = user_input.get(CONF_CHAT_MODEL)
            if model == " " or model == "" or model is None:
                errors["base"] = "model_required"
                return self.async_show_form(
                    step_id="init", data_schema=schema, errors=errors
                )

            return self.async_create_entry(title=unique_id, data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )


def common_config_option_schema(
        unique_id: str, options: MappingProxyType[str, Any]
) -> vol.Schema:
    """Return a schema for GigaChain completion options."""
    if not options:
        options = DEFAULT_OPTIONS
    schema = vol.Schema({
        vol.Optional(
            CONF_CHAT_MODEL,
            description={
                "suggested_value": options.get(CONF_CHAT_MODEL),
            },
            default="none",
        ): selector.SelectSelector(
            selector.SelectSelectorConfig(mode=SelectSelectorMode("dropdown"), options=ENGINE_MODELS[unique_id]),
        ),
        vol.Optional(
            CONF_CHAT_MODEL_USER,
            description={
                "suggested_value": options.get(CONF_CHAT_MODEL_USER)
            },
        ): str,
        vol.Optional(
            CONF_PROMPT,
            description={"suggested_value": options[CONF_PROMPT]},
            default=DEFAULT_PROMPT,
        ): TemplateSelector(),
        vol.Optional(
            CONF_TEMPERATURE,
            description={
                "suggested_value": options.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE)
            },
            default=DEFAULT_TEMPERATURE,
        ): NumberSelector(NumberSelectorConfig(min=0, max=1, step=0.05)),
        vol.Optional(
            CONF_MAX_TOKENS,
            description={
                "suggested_value": options.get(CONF_MAX_TOKENS)
            },
        ): int,
        vol.Optional(
            CONF_PROCESS_BUILTIN_SENTENCES,
            description={
                "suggested_value": options.get(CONF_PROCESS_BUILTIN_SENTENCES, DEFAULT_PROCESS_BUILTIN_SENTENCES)
            },
            default=DEFAULT_PROCESS_BUILTIN_SENTENCES): bool,
        vol.Optional(
            CONF_CHAT_HISTORY,
            description={
                "suggested_value": options.get(CONF_CHAT_HISTORY, DEFAULT_CHAT_HISTORY)
            },
            default=DEFAULT_CHAT_HISTORY): bool
    })
    if unique_id == UNIQUE_ID_GIGACHAT:
        schema = schema.extend(
            {
                vol.Optional(CONF_PROFANITY,
                             description={
                                 "suggested_value": options.get(CONF_PROFANITY, DEFAULT_PROFANITY)
                             },
                             default=DEFAULT_PROFANITY): bool
            }
        )
    if unique_id == UNIQUE_ID_ANYSCALE:
        schema = vol.Schema({
            vol.Optional(
                CONF_CHAT_MODEL,
                description={
                    "suggested_value": "Not supported anymore, please remove this entry",
                    "type": "readonly",
                },
                default="Not supported anymore",
            ): str,
        })
    return schema
