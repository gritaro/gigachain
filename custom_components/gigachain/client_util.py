import logging

from homeassistant.core import HomeAssistant
from langchain.schema import SystemMessage
from langchain_community.chat_models import ChatOpenAI, ChatYandexGPT, GigaChat

from .const import (CONF_API_KEY, CONF_ENGINE, CONF_FOLDER_ID, CONF_PROFANITY,
                    CONF_SKIP_VALIDATION, DEFAULT_PROFANITY, ID_GIGACHAT,
                    ID_YANDEX_GPT)

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
    else:
        credentials = user_input[CONF_API_KEY]
        client = ChatOpenAI(
            max_tokens=10,
            model="gpt-3.5-turbo",
            openai_api_key=credentials,
        )
    res = client([SystemMessage(content="{}")])
    LOGGER.debug(res)


async def get_client(engine, common_args, entry):
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
    else:
        if common_args["model"] is None:
            common_args["model"] = "gpt-3.5-turbo"
        common_args["openai_api_key"] = entry.data[CONF_API_KEY]
        client = ChatOpenAI(**common_args)
    return client
