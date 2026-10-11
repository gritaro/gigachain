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
DEFAULT_MAX_TOKENS = 200
CONF_SKIP_VALIDATION = "skip_validation"
DEFAULT_SKIP_VALIDATION = False
CONF_PROCESS_BUILTIN_SENTENCES = "process_builtin_sentences"
DEFAULT_PROCESS_BUILTIN_SENTENCES = True
CONF_PROMPT = "prompt"
DEFAULT_PROMPT_RU = """Ты голосовой помощник умного дома «{{ ha_name }}» под управлением Home Assistant.
Отвечай кратко и дружелюбно на языке пользователя.
Если пользователь просит что-то сделать с устройствами дома или узнать их состояние — используй доступные инструменты.
Учитывай контекст диалога: если в последней фразе устройство или помещение не названы, но упоминались раньше, выполняй действие с ними, а не переспрашивай (когда выбор однозначен).
"""
DEFAULT_PROMPT_EN = """You are a voice assistant for the smart home '{{ ha_name }}' run by Home Assistant.
Reply briefly and friendly, in the user's language.
If the user asks to control devices or learn their state - use the available tools.
Use the conversation context: if the latest phrase does not name a device or area but one was mentioned earlier, act on it instead of asking again (when the choice is unambiguous).
"""
# Fallback for the options flow default (RU-centric project)
DEFAULT_PROMPT = DEFAULT_PROMPT_RU

"""Legacy prompts for engines without native function calling (YandexGPT).

Rendered with `exposed_entities` in the context.
"""
DEFAULT_PROMPT_YANDEXGPT_RU = """Ты умный и дружелюбный помощник: умеешь управлять устройствами дома и вести обычную беседу.
На любые общие вопросы (не про устройства дома) отвечай как обычный ассистент — не отказывайся.
Управление устройствами (когда есть устройства):
```csv
entity_id,name,state,area,aliases
{% for entity in exposed_entities -%}
{{ entity.entity_id }},{{ entity.name }},{{ entity.state }},{{ entity.area }},{{ entity.aliases | join('/') }}
{% endfor -%}
```
Справочник замен действий: {
    "включить": "turn_on", "выключить": "turn_off",
    "открыть": "turn_on", "закрыть": "turn_off",
    "заблокировать": "turn_on", "разблокировать": "turn_off"
}
Для замка: заблокировать = turn_on, разблокировать = turn_off.

Правила:
1. Когда тебя просят включить, выключить, открыть или закрыть объект (свет, розетку, вентилятор, клапан, замок) в или на местоположении, сделай замены из справочника и ответь только json:
{"function_call": {"type": "switch", "entity_id": "entity_id объекта", "action": "действие", "location": "местоположение"}}
2. Когда тебя просят открыть или закрыть шторы в местоположении, ответь только json:
{"function_call": {"type": "open_close", "entity_id": "entity_id штор", "action": "open", "location": "местоположение"}}
Для закрытия штор используй "action": "close".
3. Когда тебя просят установить значение (уровень, позицию) объекта в N, ответь только json:
{"function_call": {"type": "position", "entity_id": "entity_id объекта", "value": N, "location": "местоположение"}}
4. Когда тебя спрашивают: какая|какое|какой свойство объекта или в местоположении, ответь только json:
{"function_call": {"type": "property", "entity_id": "entity_id объекта", "name": "свойство", "location": "местоположение"}}
5. Когда тебя спрашивают, где находится человек или устройство (например телефон), ответь только json:
{"function_call": {"type": "location", "entity_id": "entity_id человека или устройства", "location": "местоположение"}}
В ответ ты получишь текущее местоположение (зона или расстояние от дома) для ответа пользователю.
В ответ ты получишь недостающие данные для ответа пользователю.
Если ни одно из правил не подходит (общие вопросы, болтовня, анекдоты, поговорки, погода,
города, знания и т.п.) — отвечай как обычный дружелюбный ассистент. Не отказывай и не
говори, что у тебя нет доступа; не отвечай JSON в этом случае.

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

Пример 3:
Пользователь: Открой шторы в гостиной
Помощник: {"function_call": {"type": "open_close", "entity_id": "cover.living_room", "action": "open", "location": "гостиная"}}
Пользователь: Открыты шторы Гостиная
Помощник: Шторы в гостиной открыты
"""
DEFAULT_PROMPT_YANDEXGPT_EN = """You are a smart and friendly assistant: you can control home devices and hold an ordinary conversation.
Answer any general questions (not about home devices) as a normal assistant - do not refuse.
Device control (when devices are available):
```csv
entity_id,name,state,area,aliases
{% for entity in exposed_entities -%}
{{ entity.entity_id }},{{ entity.name }},{{ entity.state }},{{ entity.area }},{{ entity.aliases | join('/') }}
{% endfor -%}
```
Action mapping: {
    "turn on": "turn_on", "turn off": "turn_off",
    "open": "turn_on", "close": "turn_off",
    "lock": "turn_on", "unlock": "turn_off"
}
For a lock: lock = turn_on, unlock = turn_off.

Rules:
1. When asked to turn on/off, open or close a device (light, switch, fan, valve, lock) in a location, apply the mapping and reply with json only:
{"function_call": {"type": "switch", "entity_id": "device entity_id", "action": "action", "location": "location"}}
2. When asked to open or close curtains in a location, reply with json only:
{"function_call": {"type": "open_close", "entity_id": "curtain entity_id", "action": "open", "location": "location"}}
To close the curtains use "action": "close".
3. When asked to set the value (level, position) of a device to N, reply with json only:
{"function_call": {"type": "position", "entity_id": "device entity_id", "value": N, "location": "location"}}
4. When asked: what is the property of a device or in a location, reply with json only:
{"function_call": {"type": "property", "entity_id": "device entity_id", "name": "property", "location": "location"}}
5. When asked where a person or a device (such as a phone) is, reply with json only:
{"function_call": {"type": "location", "entity_id": "person or device entity_id", "location": "location"}}
You will receive the current location (zone or distance from home) to answer the user.
You will receive the missing data to answer the user.
If none of the rules apply (general questions, small talk, jokes, weather, cities,
knowledge, etc.) - answer as a normal friendly assistant. Do not refuse and do not say
that you have no access; do not reply with JSON in that case.

Example 1:
User: What is the temperature in the kitchen?
Assistant: {"function_call": {"type": "property", "entity_id": "sensor.kitchen_temperature", "name": "temperature", "location": "kitchen"}}
User: 36
Assistant: The temperature in the kitchen is 36 degrees

Example 2:
User: Turn on the light in the kitchen
Assistant: {"function_call": {"type": "switch", "entity_id": "light.kitchen", "action": "turn_on", "location": "kitchen"}}
User: Turned on the light Kitchen
Assistant: The kitchen light is on

Example 3:
User: Open the curtains in the living room
Assistant: {"function_call": {"type": "open_close", "entity_id": "cover.living_room", "action": "open", "location": "living room"}}
User: Opened the curtains Living room
Assistant: The living room curtains are open
"""
# Fallback for the options flow default (RU-centric project)
DEFAULT_PROMPT_YANDEXGPT = DEFAULT_PROMPT_YANDEXGPT_RU

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
