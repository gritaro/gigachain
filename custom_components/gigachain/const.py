"""Constants for the GigaChain integration."""

from homeassistant.helpers import selector

DOMAIN = "gigachain"
CONF_ENGINE = "engine"
CONF_CHAT_MODEL = "model"
CONF_CHAT_MODEL_USER = "model_user"
DEFAULT_CHAT_MODEL = ""
CONF_TEMPERATURE = "temperature"
DEFAULT_TEMPERATURE = 0.1
CONF_PROFANITY = "profanity"
DEFAULT_PROFANITY = False
CONF_MAX_TOKENS = "max_tokens"
CONF_SKIP_VALIDATION = "skip_validation"
DEFAULT_SKIP_VALIDATION = False
CONF_PROCESS_BUILTIN_SENTENCES = "process_builtin_sentences"
DEFAULT_PROCESS_BUILTIN_SENTENCES = True
CONF_PROMPT = "prompt"
DEFAULT_PROMPT = """Ты голосовой помощник умного дома «{{ ha_name }}» под управлением Home Assistant.
Отвечай кратко и дружелюбно на языке пользователя.
Если пользователь просит что-то сделать с устройствами дома или узнать их состояние — используй доступные инструменты.
"""

"""Legacy prompt for engines without native function calling (YandexGPT).

Rendered with `exposed_entities` in the context.
"""
DEFAULT_PROMPT_YANDEXGPT = """Ты помощник в умном доме. Есть устройства:
```csv
entity_id,name,state,area,aliases
{% for entity in exposed_entities -%}
{{ entity.entity_id }},{{ entity.name }},{{ entity.state }},{{ entity.area }},{{ entity.aliases | join('/') }}
{% endfor -%}
```
Справочник замен действий: {
    "включить": "turn_on",
    "выключить": "turn_off"
}

Есть несколько правил.
1. Когда тебя просят включить или выключить объект в или на местоположении, сделай замены из справочника и ответь только json:
{"function_call": {"type": "switch", "entity_id": "entity_id объекта", "action": "действие", "location": "местоположение"}}
2. Когда тебя спрашивают: какая|какое|какой свойство в или на местоположении, ответь только json:
{"function_call": {"type": "property", "entity_id": "entity_id объекта", "name": "свойство", "location": "местоположение"}}
В ответ ты получишь недостающие данные для ответа пользователю.
Если ни одно из правил не подходит - просто общайся с пользователем.

Пример 1:
Пользователь: Какая температура в кухне?
Помощник: {"function_call": {"type": "property", "entity_id": "sensor.kitchen_temperature", "name": "температура", "location": "кухня"}}
Пользователь: 36
Помощник: Температура в кухне 36 градусов

Пример 2:
Пользователь: Включи свет на кухне
Помощник: {"function_call": {"type": "switch", "entity_id": "light.kitchen", "action": "turn_on", "location": "кухня"}}
Пользователь: Включен свет Кухня
Помощник: Свет на кухне включен
"""

CONF_LLM_HASS_API = "llm_hass_api"
DEFAULT_LLM_HASS_API = "assist"
LLM_API_NONE = "none"

"""Models specific constants"""

ID_GIGACHAT = "gigachat"
ID_YANDEX_GPT = "yandexgpt"
ID_OPENAI = "openai"
ID_ANYSCALE = "anyscale"
UNIQUE_ID_GIGACHAT = "GigaChat"
UNIQUE_ID_YANDEX_GPT = "YandexGPT"
UNIQUE_ID_OPENAI = "OpenAI"
UNIQUE_ID_ANYSCALE = "Anyscale"

UNIQUE_ID = {
    ID_GIGACHAT: UNIQUE_ID_GIGACHAT,
    ID_YANDEX_GPT: UNIQUE_ID_YANDEX_GPT,
    ID_OPENAI: UNIQUE_ID_OPENAI,
    ID_ANYSCALE: UNIQUE_ID_ANYSCALE
}

CONF_ENGINE_OPTIONS = [
    selector.SelectOptionDict(value=ID_GIGACHAT, label=UNIQUE_ID_GIGACHAT),
    selector.SelectOptionDict(value=ID_YANDEX_GPT, label=UNIQUE_ID_YANDEX_GPT),
    selector.SelectOptionDict(value=ID_OPENAI, label=UNIQUE_ID_OPENAI),
]
MODELS_GIGACHAT = [
    " ",
    "GigaChat-2",
    "GigaChat-2-Max",
    "GigaChat-2-Pro",
    "GigaChat-3-Lightning",
    "GigaChat-3-Pro",
    "GigaChat-3-Ultra",
]
DEFAULT_MODELS_YANDEX_GPT = [" ", "YandexGPT", "YandexGPT Lite", "Summary"]
MODELS_ANYSCALE = [" ",
                           "meta-llama/Meta-Llama-3-8B-Instruct",
                           "codellama/CodeLlama-34b-Instruct-hf",
                           "Open-Orca/Mistral-7B-OpenOrca",
                           "mistralai/Mixtral-8x7B-Instruct-v0.1",
                           "HuggingFaceH4/zephyr-7b-beta",
                           "BAAI/bge-large-en-v1.5",
                           "mlabonne/NeuralHermes-2.5-Mistral-7B",
                           "meta-llama/Llama-2-13b-chat-hf", "meta-llama/Llama-2-70b-chat-hf",
                           "thenlper/gte-large", "Meta-Llama/Llama-Guard-7b", "meta-llama/Llama-2-7b-chat-hf",
                           "codellama/CodeLlama-70b-Instruct-hf", "mistralai/Mistral-7B-Instruct-v0.1"]
MODELS_OPENAI = ["gpt-4",
                         "gpt-4-0314",
                         "gpt-4-0613",
                         "gpt-4-32k",
                         "gpt-4-32k-0314",
                         "gpt-4-32k-0613",
                         "gpt-3.5-turbo",
                         "gpt-3.5-turbo-0301",
                         "gpt-3.5-turbo-0613",
                         "gpt-3.5-turbo-16k",
                         "gpt-3.5-turbo-16k-0613",
                 "gpt-3.5-turbo-instruct",
                 "text-ada-001",
                 "ada",
                 "text-babbage-001",
                 "babbage",
                 "text-curie-001",
                 "curie",
                 "davinci",
                 "text-davinci-003",
                 "text-davinci-002",
                 "code-davinci-002",
                 "code-davinci-001",
                 "code-cushman-002",
                 "code-cushman-001"]
ENGINE_MODELS = {
    UNIQUE_ID_GIGACHAT: MODELS_GIGACHAT,
    UNIQUE_ID_YANDEX_GPT: DEFAULT_MODELS_YANDEX_GPT,
    UNIQUE_ID_OPENAI: MODELS_OPENAI,
    UNIQUE_ID_ANYSCALE: MODELS_ANYSCALE
}
DEFAULT_MODEL = {
    ID_GIGACHAT: None,
    ID_OPENAI: "gpt-3.5-turbo",
    ID_YANDEX_GPT: None,
    ID_ANYSCALE: "meta-llama/Meta-Llama-3-8B-Instruct"
}

CONF_API_KEY = "api_key"
CONF_FOLDER_ID = "folder_id"
