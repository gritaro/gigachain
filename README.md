[![en](https://img.shields.io/badge/lang-en-green.svg)](https://github.com/gritaro/gigachain/blob/main/README.md)
[![ru](https://img.shields.io/badge/lang-ru-red.svg)](https://github.com/gritaro/gigachain/blob/main/README-ru.md)
<br />
<div align="center">

  <a href="https://github.com/ai-forever/gigachain">
    <img src="https://raw.githubusercontent.com/gritaro/gigachain/main/static/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h1 align="center">🦜️🔗 GigaChain (GigaChat + LangChain)</h1>
</div>

# GigaChain integration with Home Assistant
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![HACS Action](https://github.com/gritaro/gigachain/actions/workflows/hacs.yaml/badge.svg)](https://github.com/gritaro/gigachain/actions/workflows/hacs.yaml)
[![Validate with hassfest](https://github.com/gritaro/gigachain/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/gritaro/gigachain/actions/workflows/hassfest.yaml)
[![Generic badge](https://img.shields.io/github/v/release/gritaro/gigachain)](https://github.com/gritaro/gigachain)
[![Downloads for latest release](https://img.shields.io/github/downloads/gritaro/gigachain/latest/total.svg)](https://github.com/gritaro/gigachain/releases/latest)
[![Github All Releases](https://img.shields.io/github/downloads/gritaro/gigachain/total.svg)](https://github.com/gritaro/gigachain/releases)

This integration implements Voice Assistant for Home Assistant using GigaChain framework.
Currently supported LMMs:
* [GigaChat](#GigaChat) (<a href="https://developers.sber.ru/docs/ru/gigachat/overview">Sber LLM</a>)
* [YandexGPT](#YandexGPT)
* [OpenAI](#OpenAI) aka ChatGPT (not tested)

## Installation
Install it like any other HACS integration.

### Requirements
Home Assistant with installed [HACS](https://hacs.xyz/)

### Installation with HACS
Find GigaChain in HACS store. If you can't find it in store, you could [add this url as HACS custom repository](https://hacs.xyz/docs/faq/custom_repositories).

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/gritaro/gigachain)

Restart Home Assistant.

## Add Integration

[![Open your Home Assistant instance and start setting up a new integration of a specific brand.](https://my.home-assistant.io/badges/brand.svg)](https://my.home-assistant.io/redirect/brand/?brand=+GigaChain)


After adding, configure integration.

## Settings
### GigaChat
### GigaChat Authorization
You need to register at https://developers.sber.ru/studio and get an "authorization data" key.

> [!NOTE]
> You can find more details in GigaChat  [official documentation](https://developers.sber.ru/docs/en/gigachat/api/integration).
> 

<img src="https://raw.githubusercontent.com/gritaro/gigachain/main/static/auth_data.jpeg" alt="Authorization data" width="40%">

### YandexGPT
<a href="https://cloud.yandex.ru/en/docs/yandexgpt/quickstart">Quick start</a>

Create <a href="https://cloud.yandex.com/en/docs/iam/operations/sa/create">service account</a> with role `ai.languageModels.user`.
Create <a href="https://cloud.yandex.com/en/docs/iam/operations/api-key/create">API key</a>.
You can find Folder ID using this <a href="https://console.cloud.yandex.com/folders">link</a>.

### OpenAI
Create API key here https://platform.openai.com/account/api-keys

## Configuration

* _Prompt template_ (template, Home Assistant <a href=https://www.home-assistant.io/docs/configuration/templating/>`template`</a>)

The starting text for the AI language model to generate new text from. 
This text can include information about your Home Assistant instance, devices, and areas and is written using [Home Assistant Templating](https://www.home-assistant.io/docs/configuration/templating/).
Default value comes from official integration <a href="https://github.com/home-assistant/core/blob/dev/homeassistant/components/openai_conversation/const.py#L5">OpenAI Conversation</a>

* _Model_ (model, `string`)

Language model is used for text generation

* _Temperature_ (temperature, `float`)

A value that determines the level of creativity and risk-taking the model should use when generating text. 
A higher temperature means the model is more likely to generate unexpected results, while a lower temperature results in more deterministic results.
 
* Max Tokens (max_tokens, `int`)

The maximum number of words or “tokens” that the AI model should generate in its completion of the prompt.

* _Process HA Builtin Sentences_ (process_builtin_sentences, `bool`)

If enabled, integration first will pass all sentences to [HA built-in sentence processor](https://www.home-assistant.io/voice_control/builtin_sentences).
This is default behaviour of default Home Assistant Voice Assistant engine which allow you to use commands something like `turn on the living room light`.
If sentence will not be recognized by HA, it will be passed further to chosen LLM.

* Chat History (chat_history, `bool`)

Keep all conversation history. 


## Using as Voice Assistant
Create and configure Voice Assistant:

<img src="https://raw.githubusercontent.com/gritaro/gigachain/main/static/voice-assistant.jpeg" alt="Voice Assistant">
