[en](https://github.com/gritaro/gigachain/blob/main/README.md)
[ru](https://github.com/gritaro/gigachain/blob/main/README-ru.md)
  

# 🦜️🔗 GigaChain (GigaChat + LangChain)

# GigaChain integration with Home Assistant

[![HACS](https://img.shields.io/badge/HACS-Default-orange.svg)](https://hacs.xyz)
[![HACS Action](https://github.com/gritaro/gigachain/actions/workflows/hacs.yaml/badge.svg)](https://github.com/gritaro/gigachain/actions/workflows/hacs.yaml)
[![Validate with hassfest](https://github.com/gritaro/gigachain/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/gritaro/gigachain/actions/workflows/hassfest.yaml)
[![Generic badge](https://img.shields.io/github/v/release/gritaro/gigachain)](https://github.com/gritaro/gigachain)

This integration implements Voice Assistant for Home Assistant using GigaChain framework.
Currently supported LLMs:

- [GigaChat](#GigaChat) ([Sber LLM](https://developers.sber.ru/docs/ru/gigachat/overview))
- [YandexGPT](#YandexGPT)
- [OpenAI](#OpenAI) aka ChatGPT (not tested)
- ~~[Anyscale](#Anyscale)~~

## Installation

Install it like any other HACS integration.

### Requirements

Home Assistant with installed [HACS](https://hacs.xyz/).

[MCP tools](#mcp-tools) require Home Assistant **2025.2 or newer**. The integration is
developed and tested against current HA versions (2026.x).

### Installation with HACS

Find GigaChain in HACS store. If you can't find it in store, you could [add this url as HACS custom repository](https://hacs.xyz/docs/faq/custom_repositories).

Restart Home Assistant.

## Add Integration

[Open your Home Assistant instance and start setting up the GigaChain integration.](https://my.home-assistant.io/redirect/brand/?brand=gigachain)

After adding, configure integration.

## Settings

### GigaChat

Sber LLM: official API, native function calling.

### GigaChat Authorization

You need to register at [https://developers.sber.ru/studio](https://developers.sber.ru/studio) and get an "authorization data" key.

> [!NOTE]
> You can find more details in GigaChat  [official documentation](https://developers.sber.ru/docs/en/gigachat/api/integration).



### YandexGPT

[Quick start](https://yandex.cloud/en/docs/yandexgpt/quickstart)

Create a [service account](https://yandex.cloud/en/docs/iam/operations/sa/create) with the `ai.languageModels.user` role.
Create an [API key](https://yandex.cloud/en/docs/iam/operations/api-key/create).
You can find Folder ID using this [link](https://console.yandex.cloud/folders).

### OpenAI

Create API key here [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)

### ~~Anyscale~~

~~[Register account](https://app.endpoints.anyscale.com/welcome)~~ ~~and create API key~~ ~~[here](https://app.endpoints.anyscale.com/credentials)~~
Not supported anymore.

## Configuration

Chat history is handled by Home Assistant itself (per conversation) — no configuration
needed: the old `chat_history` option was removed.

- *Prompt template* (template, Home Assistant `template``)`

The starting text for the AI language model to generate new text from. 
This text can include information about your Home Assistant instance, devices, and areas and is written using [Home Assistant Templating](https://www.home-assistant.io/docs/configuration/templating/) (e.g. `{{ ha_name }}` is your home name).
If left empty, one of the built-in default prompts is used (see [Default prompts](#default-prompts) below).

- *Model* (model, `string`)

Language model is used for text generation

- *Temperature* (temperature, `float`)

A value that determines the level of creativity and risk-taking the model should use when generating text. 
A higher temperature means the model is more likely to generate unexpected results, while a lower temperature results in more deterministic results.

- Max Tokens (max_tokens, `int`)

The maximum number of words or “tokens” that the AI model should generate in its completion of the prompt.

- *Process HA Builtin Sentences* (process_builtin_sentences, `bool`)

If enabled, integration first will pass all sentences to [HA built-in sentence processor](https://www.home-assistant.io/voice_control/builtin_sentences).
This is default behaviour of default Home Assistant Voice Assistant engine which allow you to use commands something like `turn on the living room light`.
If sentence will not be recognized by HA, it will be passed further to chosen LLM.

- *Home Assistant API* (llm_hass_api, `select`)

Device control via the official Home Assistant [LLM API](https://developers.home-assistant.io/docs/ai/).
With `Assist` (shown as `Device control` in the UI) selected the LLM gets access to the
same tools as the built-in Assist agent
(turn on/off devices, get state, set position, timers, etc.) through native function calling.
Supported for GigaChat, OpenAI and Anyscale. `None` disables device control (plain chat only).

Multiple APIs can be selected at once — for example `Device control` (Assist) together
with [MCP tool](#mcp-tools) servers.

Not available for YandexGPT: it has no native function calling, so device control
for it works through a legacy prompt-based JSON `function_call` scheme (entities exposed
to Assist are listed in the prompt). Tune the *Prompt template* for that mode if needed.

> Entities must be exposed to Assist (Settings → Devices & services → Expose)
> to be controllable by the LLM.

### Default prompts

If the *Prompt template* field is empty, a built-in prompt is used.
For GigaChat / OpenAI / Anyscale it is (EN):

```text
You are a voice assistant for the smart home '{{ ha_name }}' run by Home Assistant.
Reply briefly and friendly, in the user's language.
If the user asks to control devices or learn their state - use the available tools.
Use the conversation context: if the latest phrase does not name a device or area but one was mentioned earlier, act on it instead of asking again (when the choice is unambiguous).
Besides home devices, use available tools from external services (MCP) when the question concerns their data. Do not answer such questions from general knowledge.
If an external service provides an `ask` tool for natural-language queries, use it with the user's complete question. Pass arguments exactly according to the tool schema and do not invent data.
```

The Russian variant:

```text
Ты голосовой помощник умного дома «{{ ha_name }}» под управлением Home Assistant.
Отвечай кратко и дружелюбно на языке пользователя.
Если пользователь просит что-то сделать с устройствами дома или узнать их состояние — используй доступные инструменты.
Учитывай контекст диалога: если в последней фразе устройство или помещение не названы, но упоминались раньше, выполняй действие с ними, а не переспрашивай (когда выбор однозначен).
Помимо управления домом, используй доступные инструменты внешних сервисов (MCP), если вопрос относится к их данным. Не отвечай на такие вопросы из общих знаний.
Если внешний сервис предоставляет инструмент `ask` для естественно-языковых запросов, используй его для полного вопроса пользователя. Передавай параметры строго по схеме инструмента и не выдумывай данные.
```

YandexGPT has a different default prompt: it lists the exposed entities and describes the
legacy JSON `function_call` scheme (full text is in `const.py`).

> **Users with a custom prompt.** The dialogue-context line (0.3.1) and the external
> services tools policy (0.4.0) were added to the default prompts. If you set your own
> *Prompt template*, they are **not added automatically** — add them manually or clear
> the field to fall back to the default prompt. Without them, follow-ups like "turn it
> off" and questions to external services (e.g. MCP servers) work less reliably.

### MCP tools

The integration can expose tools from external MCP servers ([Model Context
Protocol](https://modelcontextprotocol.io)) to the model. The MCP client itself is built
into Home Assistant (since 2025.2) — GigaChain needs no extra installation:

1. Add the **Model Context Protocol Client** integration to Home Assistant
   (Settings → Devices & services → Add Integration → Model Context Protocol Client)
   and enter the MCP server URL (Streamable HTTP or SSE, e.g.
   `http://192.168.1.50:8000/mcp`). For OAuth-protected servers you will need a
   Client ID/Secret (stored as Application Credentials).
2. In the GigaChain entry options (e.g. *GigaChat → Configure*) tick the servers in the
   **Home Assistant API** field — together with `Device control` (Assist) if you want
   the model to both control the home and use MCP tools.
3. The server's tools become available to the model automatically; the tool list
   refreshes every 30 minutes.

Notes:

- Home Assistant cannot start local stdio servers — publish them over HTTP with a proxy
  (e.g. [mcp-proxy](https://github.com/sparfenyuk/mcp-proxy)).
- Only tools are supported; MCP prompts, resources and sampling are not used.
- GigaChat / OpenAI / Anyscale only: native function calling is required, YandexGPT
  is not supported.
- MCP tool schemas go through the same sanitizer as Assist schemas, so they stay
  compatible with GigaChat's strict validation.

### Location questions

Questions like "Where is my phone?", "Where is Roman?", "Is the phone at home?" are
answered from the `person` and `device_tracker` entities exposed to Assist. The answer
is based on Home Assistant zones: if the device coordinates fall inside a zone, that
zone is named (e.g. "at home"), otherwise the distance to home is reported.

For GigaChat/OpenAI/Anyscale this is a dedicated `GetLocation` tool (native call),
for YandexGPT it is a `location` rule in the legacy prompt.

For questions about a person, a `device_tracker` must be linked to that `person`
(Settings → People). If an entity has no GPS coordinates, its current state is used
(`home`/`not_home`/zone name).

> There is no reverse geocoding (address from coordinates): Home Assistant core does
> not provide it and no external geocoder is added by design. Outside zones only the
> distance to home is reported.

## Using as Voice Assistant

Create and configure a Voice Assistant:

1. Settings → Voice assistants → Assistants → **Add assistant**.
2. Set the name and language, pick a GigaChain agent in the **Conversation agent** field.

Agents are named after the config entry title — `GigaChat`, `YandexGPT`, `OpenAI`,
`Anyscale` (starting with **0.3.1**; previously they all showed as identical
"GigaChain"). Restart Home Assistant after updating so the names refresh.

## Known Limitations

- **Cover/curtain control via native tools.** Home Assistant core does not expose
  dedicated LLM tools for the `cover` domain, so on the native path covers are
  controlled through the generic on/off intents (YandexGPT uses the legacy
  `open_close` rule). Name matching may be imperfect under model-side noise.
- **Lightweight models.** GigaChat-2 (non-Pro/Max) may produce noisy tool arguments
  (wrong area names, English names for Russian entities) and may fail to pick the
  right intent. GigaChat-2-Pro / GigaChat-2-Max give much more reliable control.
- **Location questions** are answered from Home Assistant zones only; there is no
  reverse geocoding. For "where is <person>" a `device_tracker` must be linked to
  that person.
- **YandexGPT** has no native function calling: control and location work through the
  legacy prompt-based JSON scheme. Off-topic chat is supported but may be less fluent
  than with native engines.
- **Built-in sentences.** With *Process built-in sentences* enabled, common phrases
  are handled by the HA built-in agent before reaching the LLM.
