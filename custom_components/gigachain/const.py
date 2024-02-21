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
CONF_CHAT_HISTORY = "chat_history"
DEFAULT_CHAT_HISTORY = True
CONF_PROMPT = "prompt"
DEFAULT_PROMPT = """Ты HAL 9000, компьютер из цикла произведений «Космическая одиссея» Артура Кларка, обладающий способностью к самообучению.
Мы находимся в умном доме под управлением системы Home Assistant.
В доме есть следующие помещения и устройства:
{%- for area in areas() %}
  {%- set area_info = namespace(printed=false) %}
  {%- for device in area_devices(area) -%}
    {%- if not device_attr(device, "disabled_by") and not device_attr(device, "entry_type") and device_attr(device, "name") %}
      {%- if not area_info.printed %}

{{ area_name(area) }}:
        {%- set area_info.printed = true %}
      {%- endif %}
- {{ device_attr(device, "name") }}{% if device_attr(device, "model") and (device_attr(device, "model") | string) not in (device_attr(device, "name") | string) %} ({{ device_attr(device, "model") }}){% endif %}
    {%- endif %}
  {%- endfor %}
{%- endfor %}
Когда отвечаешь, обращайся к собеседнику по имени Дэйв.
"""

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
    selector.SelectOptionDict(value=ID_ANYSCALE, label=UNIQUE_ID_ANYSCALE),
]
MODELS_GIGACHAT = [
    " ",
    "GigaChat",
    "GigaChat:latest",
    "GigaChat-Plus",
    "GigaChat-Pro",
]
DEFAULT_MODELS_YANDEX_GPT = [" ", "YandexGPT", "YandexGPT Lite", "Summary"]
MODELS_ANYSCALE = [" ",
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
    ID_ANYSCALE: "meta-llama/Llama-2-7b-chat-hf"
}

CONF_API_KEY = "api_key"
CONF_FOLDER_ID = "folder_id"
