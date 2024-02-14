"""The GigaChain integration."""
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
from langchain_community.chat_models import GigaChat, ChatYandexGPT, ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from homeassistant.util import ulid
from .const import (
    DOMAIN,
    CONF_ENGINE,
    CONF_TEMPERATURE,
    DEFAULT_TEMPERATURE,
    CONF_CHAT_MODEL,
    DEFAULT_CHAT_MODEL,
    CONF_CHAT_MODEL,
    CONF_FOLDER_ID,
    CONF_API_KEY,
    CONF_CHAT_MODEL,
    DEFAULT_CHAT_MODEL,
    CONF_PROMPT,
    DEFAULT_PROMPT
    )
import logging

LOGGER = logging.getLogger(__name__)

async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Initialize GigaChain."""
    temperature = entry.options.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE)
    model = entry.options.get(CONF_CHAT_MODEL)
    engine = entry.data.get(CONF_ENGINE) or "gigachat"
    entry.async_on_unload(entry.add_update_listener(update_listener))
    if engine == 'gigachat':
        client = GigaChat(temperature=temperature,
                          model=model,
                          verbose=True,
                          credentials=entry.data[CONF_API_KEY],
                          verify_ssl_certs=False)
    elif engine == 'yandexgpt':
        if model == "YandexGPT":
            model_url = "gpt://" + entry.data[CONF_FOLDER_ID] + "/yandexgpt/latest"
        elif model == 'YandexGPT Lite':
            model_url = "gpt://" + entry.data[CONF_FOLDER_ID] + "/yandexgpt-lite/latest"
        elif model == 'Summary':
            model_url = "gpt://" + entry.data[CONF_FOLDER_ID] + "/summarization/latest"
        else:
            model_url = ""
        client = ChatYandexGPT(
                               model_uri=model_url,
                               temperature=temperature,
                               api_key=entry.data[CONF_API_KEY],
                               folder_id = entry.data[CONF_FOLDER_ID])
    else:
        client = ChatOpenAI(model=model,
                            temperature=temperature,
                            openai_api_key=entry.data[CONF_API_KEY])
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
