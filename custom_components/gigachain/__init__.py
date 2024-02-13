"""The GigaChain integration."""
from __future__ import annotations
from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    intent,
    template,
)
from homeassistant.components.conversation import AgentManager, agent
from typing import Literal
from langchain_community.chat_models import GigaChat
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from homeassistant.util import ulid
from .const import (
    DOMAIN,
    CONF_AUTH_DATA,
    CONF_CHAT_MODEL,
    DEFAULT_CHAT_MODEL,
    CONF_PROMPT,
    DEFAULT_PROMPT
    )
import logging

LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Initialize GigaChain."""
    client = GigaChat(credentials=entry.data[CONF_AUTH_DATA], verify_ssl_certs=False)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = client
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
        self.history: dict[str, list[dict]] = {}

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return a list of supported languages."""
        return MATCH_ALL

    async def async_process(
        self, user_input: agent.ConversationInput
    ) -> agent.ConversationResult:
        """Process a sentence."""
        raw_prompt = self.entry.options.get(CONF_PROMPT, DEFAULT_PROMPT)
        model = self.entry.options.get(CONF_CHAT_MODEL, DEFAULT_CHAT_MODEL)
        if user_input.conversation_id in self.history:
            conversation_id = user_input.conversation_id
            messages = self.history[conversation_id]
        else:
            conversation_id = ulid.ulid_now()
            prompt = self._async_generate_prompt(raw_prompt)
            messages = [
                SystemMessage(
                content=prompt
                )
            ]

        messages.append(HumanMessage(content=user_input.text))
        client = self.hass.data[DOMAIN][self.entry.entry_id]
        client.model = model

        res = client(messages)
        messages.append(res)
        self.history[conversation_id] = messages

        response = intent.IntentResponse(language=user_input.language)
        response.async_set_speech(res.content)
        return agent.ConversationResult(
            conversation_id=conversation_id,
            response=response
        )

    def _async_generate_prompt(self, raw_prompt: str) -> str:
        """Generate a prompt for the user."""
        return template.Template(raw_prompt, self.hass).async_render(
            {
                "ha_name": self.hass.config.location_name,
            },
            parse_result=False,
        )
