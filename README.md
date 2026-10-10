[en](https://github.com/gritaro/gigachain/blob/main/README.md)
[ru](https://github.com/gritaro/gigachain/blob/main/README-ru.md)
  




Fixed Version 2026.5

# 🦜️🔗 GigaChain (GigaChat + LangChain)

# GigaChain integration with Home Assistant

[HACS](https://hacs.xyz)
[HACS Action](https://github.com/gritaro/gigachain/actions/workflows/hacs.yaml)
[Validate with hassfest](https://github.com/gritaro/gigachain/actions/workflows/hassfest.yaml)
[Generic badge](https://github.com/gritaro/gigachain)
[Downloads for latest release](https://github.com/gritaro/gigachain/releases/latest)
[Github All Releases](https://github.com/gritaro/gigachain/releases)

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

Chat history is now handled by Home Assistant itself (per conversation), the old
`chat_history` option was removed.

## Using as Voice Assistant

Create and configure Voice Assistant:

