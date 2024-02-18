"""The GigaChain integration."""

import logging
from typing import Literal

from homeassistant.components import conversation
from homeassistant.components.conversation import agent
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent, template
from homeassistant.util import ulid
from langchain.schema import BaseMessage, HumanMessage, SystemMessage

from .client_util import get_client
from .const import (CONF_API_KEY, CONF_CHAT_MODEL, CONF_CHAT_MODEL_USER,
                    CONF_ENGINE, CONF_FOLDER_ID, CONF_MAX_TOKENS,
                    CONF_PROFANITY, CONF_PROMPT, CONF_TEMPERATURE,
                    DEFAULT_CHAT_MODEL, DEFAULT_PROFANITY, DEFAULT_PROMPT,
                    DEFAULT_TEMPERATURE, DOMAIN, ID_GIGACHAT)

LOGGER = logging.getLogger(__name__)


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Initialize GigaChain."""
    engine = entry.data.get(CONF_ENGINE) or ID_GIGACHAT
    model = entry.options.get(CONF_CHAT_MODEL_USER)
    if model == " " or model == "" or model is None:
        model = entry.options.get(CONF_CHAT_MODEL)
    temperature = entry.options.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE)
    max_tokens = entry.options.get(CONF_MAX_TOKENS)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    common_args = {
        "verbose": False,
        "model": model
    }
    if temperature is not None:
        common_args["temperature"] = temperature
    if max_tokens is not None:
        common_args["max_tokens"] = max_tokens

    _client = await get_client(engine, common_args, entry)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = _client
    conversation.async_set_agent(hass, entry, GigaChatAI(hass, entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload GigaChain."""
    hass.data[DOMAIN].pop(entry.entry_id)
    conversation.async_unset_agent(hass, entry)
    return True


class GigaChatAI(conversation.AbstractConversationAgent):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the agent."""
        self.hass = hass
        self.entry = entry
        self.history: dict[str, list[BaseMessage]] = {}

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return a list of supported languages."""
        return MATCH_ALL

    async def async_process(
            self, user_input: agent.ConversationInput
    ) -> agent.ConversationResult:
        """Process a sentence."""
        raw_prompt = self.entry.options.get(CONF_PROMPT, DEFAULT_PROMPT)
        if user_input.conversation_id in self.history:
            conversation_id = user_input.conversation_id
            messages = self.history[conversation_id]
        else:
            conversation_id = ulid.ulid()
            prompt = self._async_generate_prompt(raw_prompt)
            messages = [SystemMessage(content=prompt)]
        messages.append(HumanMessage(content=user_input.text))
        _client = self.hass.data[DOMAIN][self.entry.entry_id]

        try:
            res = _client(messages)
        except Exception as err:
            LOGGER.exception("Unexpected exception %s", type(err))
            response = intent.IntentResponse(language=user_input.language)
            response.async_set_error(
                intent.IntentResponseErrorCode.UNKNOWN,
                f"Houston we have a problem: {err}",
            )
            return agent.ConversationResult(
                conversation_id=conversation_id, response=response
            )

        messages.append(res)
        self.history[conversation_id] = messages
        LOGGER.debug(messages)

        response = intent.IntentResponse(language=user_input.language)
        response.async_set_speech(res.content)
        LOGGER.debug(response)
        return agent.ConversationResult(
            conversation_id=conversation_id, response=response
        )

    def _async_generate_prompt(self, raw_prompt: str) -> str:
        """Generate a prompt for the user."""
        return template.Template(raw_prompt, self.hass).async_render(
            {
                "ha_name": self.hass.config.location_name,
            },
            parse_result=False,
        )
