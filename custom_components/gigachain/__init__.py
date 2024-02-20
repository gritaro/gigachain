"""The GigaChain integration."""

import logging
from typing import Literal

from home_assistant_intents import get_languages
from homeassistant.components import conversation
from homeassistant.components.conversation import agent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent, template
from homeassistant.util import ulid
from langchain.schema import BaseMessage, HumanMessage, SystemMessage, AIMessage

from .client_util import get_client
from .const import (CONF_API_KEY, CONF_CHAT_MODEL, CONF_CHAT_MODEL_USER,
                    CONF_ENGINE, CONF_FOLDER_ID, CONF_MAX_TOKENS,
                    CONF_PROFANITY, CONF_PROMPT, CONF_TEMPERATURE,
                    DEFAULT_CHAT_MODEL, DEFAULT_PROFANITY, DEFAULT_PROMPT,
                    CONF_PROCESS_BUILTIN_SENTENCES, DEFAULT_PROCESS_BUILTIN_SENTENCES,
                    CONF_CHAT_HISTORY, DEFAULT_CHAT_HISTORY,
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
    _agent = GigaChatAI(hass, entry)
    await _agent.async_initialize(
        hass.data.get("conversation_config")
    )
    conversation.async_set_agent(hass, entry, _agent)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload GigaChain."""
    hass.data[DOMAIN].pop(entry.entry_id)
    conversation.async_unset_agent(hass, entry)
    return True


class GigaChatAI(conversation.DefaultAgent):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the agent."""
        super().__init__(hass)
        self.hass = hass
        self.entry = entry
        self.history: dict[str, list[BaseMessage]] = {}

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return a list of supported languages."""
        return get_languages()

    async def async_process(
            self, user_input: agent.ConversationInput
    ) -> agent.ConversationResult:
        """Process a sentence."""
        raw_prompt = self.entry.options.get(CONF_PROMPT, DEFAULT_PROMPT)
        chat_history_enabled = self.entry.options.get(CONF_CHAT_HISTORY, DEFAULT_CHAT_HISTORY)

        if user_input.conversation_id in self.history and chat_history_enabled:
            conversation_id = user_input.conversation_id
            messages = self.history[conversation_id]
        else:
            conversation_id = ulid.ulid()
            prompt = self._async_generate_prompt(raw_prompt)
            messages = [SystemMessage(content=prompt)]

        messages.append(HumanMessage(content=user_input.text))

        use_builtin_sentences = self.entry.options.get(CONF_PROCESS_BUILTIN_SENTENCES,
                                                       DEFAULT_PROCESS_BUILTIN_SENTENCES)
        if use_builtin_sentences:
            default_agent_response = await super(GigaChatAI, self).async_process(user_input)

            if default_agent_response.response.intent:
                messages.append(AIMessage(content=default_agent_response.response.speech.get("plain").get("speech")))
                self.history[conversation_id] = messages
                return agent.ConversationResult(
                    conversation_id=conversation_id, response=default_agent_response.response
                )

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
        LOGGER.info(messages)

        response = intent.IntentResponse(language=user_input.language)
        response.async_set_speech(res.content)
        LOGGER.info(response)
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
