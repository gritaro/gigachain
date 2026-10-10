[en](https://github.com/gritaro/gigachain/blob/main/README.md)
[ru](https://github.com/gritaro/gigachain/blob/main/README-ru.md)
  




Fixed Version 2026.5

# 🦜️🔗 GigaChain (GigaChat + LangChain)

# GigaChain integration with Home Assistant

[![HACS](https://img.shields.io/badge/HACS-Default-orange.svg)](https://hacs.xyz)
[![HACS Action](https://github.com/gritaro/gigachain/actions/workflows/hacs.yaml/badge.svg)](https://github.com/gritaro/gigachain/actions/workflows/hacs.yaml)
[![Validate with hassfest](https://github.com/gritaro/gigachain/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/gritaro/gigachain/actions/workflows/hassfest.yaml)
[![Generic badge](https://img.shields.io/github/v/release/gritaro/gigachain)](https://github.com/gritaro/gigachain)
[![Downloads for latest release](https://img.shields.io/github/downloads/gritaro/gigachain/latest/total)](https://github.com/gritaro/gigachain/releases/latest)
[![Github All Releases](https://img.shields.io/github/downloads/gritaro/gigachain/total)](https://github.com/gritaro/gigachain/releases)

This integration implements Voice Assistant for Home Assistant using GigaChain framework.
Currently supported LMMs:

- [GigaChat](#GigaChat) ([Sber LLM](https://developers.sber.ru/docs/ru/gigachat/overview))
- [YandexGPT](#YandexGPT)
- [OpenAI](#OpenAI) aka ChatGPT (not tested)
- ~~[Anyscale](#Anyscale)~~

## Installation

Install it like any other HACS integration.

### Requirements

Home Assistant with installed [HACS](https://hacs.xyz/)

### Installation with HACS

Find GigaChain in HACS store. If you can't find it in store, you could [add this url as HACS custom repository](https://hacs.xyz/docs/faq/custom_repositories).

[hacs_badge](https://github.com/gritaro/gigachain)

Restart Home Assistant.

## Add Integration

[Open your Home Assistant instance and start setting up a new integration of a specific brand.](https://my.home-assistant.io/redirect/brand/?brand=+GigaChain)

After adding, configure integration.

## Settings

### GigaChat

### GigaChat Authorization

You need to register at [https://developers.sber.ru/studio](https://developers.sber.ru/studio) and get an "authorization data" key.

> [!NOTE]
> You can find more details in GigaChat  [official documentation](https://developers.sber.ru/docs/en/gigachat/api/integration).



### YandexGPT

[Quick start](https://cloud.yandex.ru/en/docs/yandexgpt/quickstart)

Create [service account](https://cloud.yandex.com/en/docs/iam/operations/sa/create) with role `ai.languageModels.user`.
Create [API key](https://cloud.yandex.com/en/docs/iam/operations/api-key/create).
You can find Folder ID using this [link](https://console.cloud.yandex.com/folders).

### OpenAI

Create API key here [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)

### ~~Anyscale~~

~~[Register account](https://app.endpoints.anyscale.com/welcome)~~ ~~and create API key~~ ~~[here](https://app.endpoints.anyscale.com/credentials)~~
Not supported anymore.

## Configuration

- *Prompt template* (template, Home Assistant `template``)`

The starting text for the AI language model to generate new text from. 
This text can include information about your Home Assistant instance, devices, and areas and is written using [Home Assistant Templating](https://www.home-assistant.io/docs/configuration/templating/).
Default value comes from official integration [OpenAI Conversation](https://github.com/home-assistant/core/blob/dev/homeassistant/components/openai_conversation/const.py#L5)

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
With `Assist` selected the LLM gets access to the same tools as the built-in Assist agent
(turn on/off devices, get state, set position, timers, etc.) through native function calling.
Supported for GigaChat, OpenAI and Anyscale. `None` disables device control (plain chat only).

Not available for YandexGPT: it has no native function calling, so device control
for it works through a legacy prompt-based JSON `function_call` scheme (entities exposed
to Assist are listed in the prompt). Tune the *Prompt template* for that mode if needed.

> Entities must be exposed to Assist (Settings → Devices & services → Exposations)
> to be controllable by the LLM.

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

Chat history is now handled by Home Assistant itself (per conversation), the old
`chat_history` option was removed.

## Using as Voice Assistant

Create and configure Voice Assistant:

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

