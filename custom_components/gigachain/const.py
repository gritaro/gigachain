"""Constants for the GigaChain integration."""
from homeassistant.helpers import selector

DOMAIN = "gigachain"
CONF_ENGINE = "engine"
UNIQUE_ID = {"gigachat": "GigaChat", "yandexgpt": "YandexGPT", "openai": "OpenAI"}
CONF_ENGINE_OPTIONS = [
  selector.SelectOptionDict(value="gigachat", label="GigaChat"),
  selector.SelectOptionDict(value="yandexgpt", label="YandexGPT"),
  selector.SelectOptionDict(value="openai", label="OpenAI"),
]
CONF_API_KEY = "api_key"
CONF_FOLDER_ID = "folder_id"

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

CONF_CHAT_MODEL = "model"
#GigaChat-Plus,GigaChat-Pro,GigaChat:latest
DEFAULT_CHAT_MODEL = "GigaChat"
CONF_TEMPERATURE = "temperature"
DEFAULT_CONF_TEMPERATURE = "0.1"
CONF_MAX_TKNS = "max_tokens"
DEFAULT_CONF_MAX_TKNS = "250"
