import logging
import warnings

from homeassistant.core import HomeAssistant
from langchain_community.chat_models import ChatAnyscale, ChatYandexGPT
from langchain_core._api.deprecation import LangChainDeprecationWarning
from langchain_core.messages import SystemMessage
from langchain_gigachat.chat_models import GigaChat
from langchain_openai import ChatOpenAI

from .const import (
    CONF_API_KEY,
    CONF_CHAT_MODEL,
    CONF_CHAT_MODEL_USER,
    CONF_ENGINE,
    CONF_FOLDER_ID,
    CONF_PROFANITY,
    CONF_SKIP_VALIDATION,
    DEFAULT_MODEL,
    DEFAULT_PROFANITY,
    ENGINE_MODELS,
    ID_ANYSCALE,
    ID_GIGACHAT,
    ID_OPENAI,
    ID_YANDEX_GPT,
    MODELS_ANYSCALE,
    UNIQUE_ID_GIGACHAT,
    UNIQUE_ID_OPENAI,
)

LOGGER = logging.getLogger(__name__)

warnings.filterwarnings(
    "ignore",
    category=LangChainDeprecationWarning,
    message=r".*ChatOpenAI.*",
)


async def validate_client(
        hass: HomeAssistant,
        user_input
) -> None:
    if user_input.get(CONF_SKIP_VALIDATION):
        return
    await hass.async_add_executor_job(_validate_client, user_input)


def _validate_client(user_input) -> None:
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
    res = client.invoke([SystemMessage(content="{}")])
    LOGGER.debug(res)


async def get_client(hass: HomeAssistant, engine, entry, common_args):
    return await hass.async_add_executor_job(_get_client, engine, entry, common_args)


def _get_client(engine, entry, common_args):
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
            anyscale_api_key: str | None = None,
            anyscale_api_base: str | None = None,
    ) -> set[str]:
        """Get available models from configuration."""
        return MODELS_ANYSCALE


async def get_models(hass: HomeAssistant, entry) -> list[str]:
    """Fetch model list from the engine API, fall back to the static list."""
    unique_id = entry.unique_id
    if unique_id not in (UNIQUE_ID_GIGACHAT, UNIQUE_ID_OPENAI):
        return list(ENGINE_MODELS.get(unique_id, []))
    api_key = entry.data.get(CONF_API_KEY)
    current = (entry.options.get(CONF_CHAT_MODEL_USER)
               or entry.options.get(CONF_CHAT_MODEL))
    return await hass.async_add_executor_job(_fetch_models, unique_id, api_key, current)


def _fetch_models(unique_id: str, api_key: str, current: str | None) -> list[str]:
    fallback = list(ENGINE_MODELS.get(unique_id, []))
    try:
        if unique_id == UNIQUE_ID_GIGACHAT:
            from gigachat import GigaChat
            client = GigaChat(credentials=api_key, verify_ssl_certs=False, timeout=10)
            ids = [m.id for m in client.get_models().data or []]
            models = [m for m in ids
                      if not m.lower().startswith(("embeddings", "gigaembeddings"))]
        elif unique_id == UNIQUE_ID_OPENAI:
            import openai
            client = openai.OpenAI(api_key=api_key, timeout=10, max_retries=1)
            ids = [m.id for m in client.models.list().data]
            models = [m for m in ids
                      if m.startswith(("gpt-", "chatgpt", "o1", "o3", "o4"))]
        else:
            return fallback
    except Exception as err:  # noqa: BLE001
        LOGGER.debug("Cannot fetch models for %s: %s", unique_id, err)
        return fallback
    models = sorted(set(models))
    if current and current != " " and current not in models:
        models.insert(0, current)
    return [" "] + models
