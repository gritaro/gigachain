<br />
<div align="center">

  <a href="https://github.com/ai-forever/gigachain">
    <img src="https://raw.githubusercontent.com/gritaro/gigachain/main/static/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h1 align="center">🦜️🔗 GigaChain (GigaChat + LangChain)</h1>
</div>

# Компонент GigaChain для Home Assistant
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![HACS Action](https://github.com/gritaro/gigachain/actions/workflows/hacs.yaml/badge.svg)](https://github.com/gritaro/gigachain/actions/workflows/hacs.yaml)
[![Validate with hassfest](https://github.com/gritaro/gigachain/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/gritaro/gigachain/actions/workflows/hassfest.yaml)
[![Generic badge](https://img.shields.io/github/v/release/gritaro/gigachain)](https://github.com/gritaro/gigachain)
[![Downloads for latest release](https://img.shields.io/github/downloads/gritaro/gigachain/latest/total.svg)](https://github.com/gritaro/gigachain/releases/latest)
[![Github All Releases](https://img.shields.io/github/downloads/gritaro/gigachain/total.svg)](https://github.com/gritaro/gigachain/releases)

Компонент реализует диалоговую систему Home Assistant для использования с языковыми моделями, поддерживаемыми фреймворком GigaChain.
В настоящее время поддерживаются интеграции с LMM:
* [GigaChat](#GigaChat) (<a href="https://developers.sber.ru/docs/ru/gigachat/overview">русскоязычная нейросеть от Сбера</a>)
* [YandexGPT](#YandexGPT)
* [OpenAI](#OpenAI) ака ChatGPT (не тестируется)

## Установка
Устанавливается как и любая HACS интеграция.

### Необходимые требования
Для использования интеграции вам понадобится Home Assistant с установленным [HACS](https://hacs.xyz/)

### Установка с использованием HACS
Найдите GigaChain в магазине HACS. Если интеграция не находится в магазине HACS, вы можете [добавить этот url как пользовательский репозиторий HACS](https://hacs.xyz/docs/faq/custom_repositories).

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/gritaro/gigachain)

Перезапустите Home Assistant.

## Добавление интеграции

[![Open your Home Assistant instance and start setting up a new integration of a specific brand.](https://my.home-assistant.io/badges/brand.svg)](https://my.home-assistant.io/redirect/brand/?brand=+GigaChain)

После добавления настройте интеграцию.

## Настройки
### GigaChat
### Авторизация запросов к GigaChat
Для авторизации запросов к GigaChat вам понадобится получить *авторизационные данные* для работы с GigaChat API.

> [!NOTE]
> О том как получить авторизационные данные для доступа к GigaChat читайте в [официальной документации](https://developers.sber.ru/docs/ru/gigachat/api/integration).
> 

<img src="https://raw.githubusercontent.com/gritaro/gigachain/main/static/auth_data.jpeg" alt="Authorization data" width="40%">

### YandexGPT
<a href="https://cloud.yandex.ru/ru/docs/yandexgpt/quickstart">Быстрый старт</a>

Создайте <a href="https://cloud.yandex.com/en/docs/iam/operations/sa/create">сервисный аккаунт</a> с ролью `ai.languageModels.user`
Для создания аккаунта потребуется привязка карты.
Создайте <a href="https://cloud.yandex.com/en/docs/iam/operations/api-key/create">API ключ</a>
Идентификатор каталога (Folder ID) можно узнать пройдя по <a href="https://console.cloud.yandex.com/folders">ссылке</a>

### OpenAI
Для генерации ключа проследуйте по ссылке https://platform.openai.com/account/api-keys

## Конфигурация

* _Темплейт промпта_ (template, Home Assistant <a href=https://www.home-assistant.io/docs/configuration/templating/>`template`</a>)

Системное сообщение, настраивающее модель и задающее исходное поведение.
Значение по умолчанию  является лишь примером, взятым из офицальной интеграции <a href="https://github.com/home-assistant/core/blob/dev/homeassistant/components/openai_conversation/const.py#L5">OpenAI Conversation</a>
Рекомендуется его изменить под собственные нужды.

* _Модель_ (model, `string`)

Модели генерации текста в рамках выбранной LLM. Каждая модель может иметь свои тарифы.
В настоящее время выбор модели не поддерживается.

* _Температура_ (temperature, `float`)

Температура выборки. Значение температуры должно быть не меньше ноля. Чем выше значение, тем более случайным будет ответ модели. При значениях температуры больше двух, набор токенов в ответе модели может отличаться избыточной случайностью.
Значение по умолчанию зависит от выбранной модели

* Максимум токенов (max_tokens, int)

Максимальное количество токенов, которые будут использованы для создания ответов.
В настоящее время не поддерживается, используются настройки модели по умолчанию.

## Использование в качестве диалоговой системы
Создайте и настройте новый голосовой ассистент:

<img src="https://raw.githubusercontent.com/gritaro/gigachain/main/static/voice-assistant.jpeg" alt="Voice Assistant">
