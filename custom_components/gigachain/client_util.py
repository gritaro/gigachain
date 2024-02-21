import logging
from typing import Set

from homeassistant.core import HomeAssistant
from langchain.schema import SystemMessage
from langchain_community.chat_models import ChatOpenAI, ChatYandexGPT, GigaChat, ChatAnyscale

from .const import (CONF_API_KEY, CONF_ENGINE, CONF_FOLDER_ID, CONF_PROFANITY,
                    CONF_SKIP_VALIDATION, DEFAULT_PROFANITY, ID_GIGACHAT,
                    ID_YANDEX_GPT, ID_OPENAI, ID_ANYSCALE, DEFAULT_MODEL, MODELS_ANYSCALE)

LOGGER = logging.getLogger(__name__)


async def validate_client(
        hass: HomeAssistant,
        user_input
) -> None:
    if user_input.get(CONF_SKIP_VALIDATION):
        return
    engine = user_input.get(CONF_ENGINE) or ID_GIGACHAT
    if engine == ID_GIGACHAT:
        credentials = user_input[CONF_API_KEY]
        client = GigaChat(
            max_tokens=10,
            verbose=False,
            credentials=credentials,
            verify_ssl_certs=False,
        )
    elif engine == ID_YANDEX_GPT:
        client = ChatYandexGPT(
            max_tokens=10,
            max_retries=2,
            api_key=user_input[CONF_API_KEY],
            folder_id=user_input[CONF_FOLDER_ID],
        )
    elif engine == ID_ANYSCALE:
        client = LocalChatAnyscale(
            max_tokens=10,
            max_retries=2,
            model=DEFAULT_MODEL[ID_ANYSCALE],
            anyscale_api_key=user_input[CONF_API_KEY]
        )
    else:
        credentials = user_input[CONF_API_KEY]
        client = ChatOpenAI(
            max_tokens=10,
            model=DEFAULT_MODEL[ID_ANYSCALE],
            openai_api_key=credentials,
        )
    res = client([SystemMessage(content="{}")])
    LOGGER.debug(res)


async def get_client(hass: HomeAssistant, engine, entry, common_args):
    if engine == ID_GIGACHAT:
        common_args["credentials"] = entry.data[CONF_API_KEY]
        common_args["verify_ssl_certs"] = False
        common_args["profanity_check"] = entry.options.get(CONF_PROFANITY, DEFAULT_PROFANITY)
        client = GigaChat(**common_args)
    elif engine == ID_YANDEX_GPT:
        common_args["api_key"] = entry.data[CONF_API_KEY]
        common_args["folder_id"] = entry.data[CONF_FOLDER_ID]
        common_args["max_retries"] = 2
        client = ChatYandexGPT(**common_args)
    elif engine == ID_ANYSCALE:
        common_args["anyscale_api_key"] = entry.data[CONF_API_KEY]
        if common_args["model"] is None:
            common_args["model"] = DEFAULT_MODEL[ID_ANYSCALE]
        client = LocalChatAnyscale(**common_args)
    else:
        if common_args["model"] is None:
            common_args["model"] = DEFAULT_MODEL[ID_OPENAI]
        common_args["openai_api_key"] = entry.data[CONF_API_KEY]
        client = ChatOpenAI(**common_args)
    return client


class LocalChatAnyscale(ChatAnyscale):
    @staticmethod
    def get_available_models(
            anyscale_api_key: str = None,
            anyscale_api_base: str = None,
    ) -> Set[str]:
        """Get available models from configuration."""
        return MODELS_ANYSCALE
