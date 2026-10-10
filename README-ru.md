[en](https://github.com/gritaro/gigachain/blob/main/README.md)
[ru](https://github.com/gritaro/gigachain/blob/main/README-ru.md)
  

# 🦜️🔗 GigaChain (GigaChat + LangChain)

# Компонент GigaChain для Home Assistant

[![HACS](https://img.shields.io/badge/HACS-Default-orange.svg)](https://hacs.xyz)
[![HACS Action](https://github.com/gritaro/gigachain/actions/workflows/hacs.yaml/badge.svg)](https://github.com/gritaro/gigachain/actions/workflows/hacs.yaml)
[![Validate with hassfest](https://github.com/gritaro/gigachain/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/gritaro/gigachain/actions/workflows/hassfest.yaml)
[![Generic badge](https://img.shields.io/github/v/release/gritaro/gigachain)](https://github.com/gritaro/gigachain)
[![Downloads for latest release](https://img.shields.io/github/downloads/gritaro/gigachain/latest/total)](https://github.com/gritaro/gigachain/releases/latest)
[![Github All Releases](https://img.shields.io/github/downloads/gritaro/gigachain/total)](https://github.com/gritaro/gigachain/releases)

Компонент реализует диалоговую систему Home Assistant для использования с языковыми моделями, поддерживаемыми фреймворком GigaChain.
В настоящее время поддерживаются интеграции с LMM:

- [GigaChat](#GigaChat) ([русскоязычная (но не только) нейросеть от Сбера](https://developers.sber.ru/docs/ru/gigachat/overview))
- [YandexGPT](#YandexGPT)
- [OpenAI](#OpenAI) ака ChatGPT (не тестируется)
- ~~[Anyscale](#Anyscale)~~

## Установка

Устанавливается как и любая HACS интеграция.

### Необходимые требования

Для использования интеграции вам понадобится Home Assistant с установленным [HACS](https://hacs.xyz/)

### Установка с использованием HACS

Найдите GigaChain в магазине HACS. Если интеграция не находится в магазине HACS, вы можете [добавить этот url как пользовательский репозиторий HACS](https://hacs.xyz/docs/faq/custom_repositories).

[hacs_badge](https://github.com/gritaro/gigachain)

Перезапустите Home Assistant.

## Добавление интеграции

[Open your Home Assistant instance and start setting up a new integration of a specific brand.](https://my.home-assistant.io/redirect/brand/?brand=+GigaChain)

После добавления настройте интеграцию.

## Настройки

### GigaChat

### Авторизация запросов к GigaChat

Для авторизации запросов к GigaChat вам понадобится получить *авторизационные данные* для работы с GigaChat API.

> [!NOTE]
> О том как получить авторизационные данные для доступа к GigaChat читайте в [официальной документации](https://developers.sber.ru/docs/ru/gigachat/api/integration).
>
> [!NOTE]
> Сертификаты НУЦ Минцифры устанавливать не нужно



### YandexGPT

[Быстрый старт](https://cloud.yandex.ru/ru/docs/yandexgpt/quickstart)

Создайте [сервисный аккаунт](https://cloud.yandex.com/ru/docs/iam/operations/sa/create) с ролью `ai.languageModels.user`.
Для создания аккаунта потребуется привязка карты. С карты будет снята и возвращена символическая сумма (11 RUB).

Создайте [API ключ](https://cloud.yandex.com/ru/docs/iam/operations/api-key/create).
Идентификатор каталога (Folder ID) можно узнать пройдя по [ссылке](https://console.cloud.yandex.com/folders).

### OpenAI

Для генерации ключа проследуйте по ссылке [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)

### ~~Anyscale~~

~~[Зарегистрируйтесь](https://app.endpoints.anyscale.com/welcome)~~ ~~и создайте API ключ~~ ~~[здесь](https://app.endpoints.anyscale.com/credentials)~~ На данный момент не поддерживается.

## Конфигурация

- *Темплейт промпта* (template, Home Assistant `template``)`

Системное сообщение, настраивающее модель и задающее исходное поведение.
Значение по умолчанию  является лишь примером, взятым из офицальной интеграции [OpenAI Conversation](https://github.com/home-assistant/core/blob/dev/homeassistant/components/openai_conversation/const.py#L5).
Рекомендуется его изменить под собственные нужды.

- *Модель* (model, `string`)

Модели генерации текста в рамках выбранной LLM. Каждая модель может иметь свои тарифы.

- *Температура* (temperature, `float`)

Температура выборки. Значение температуры должно быть не меньше ноля. Чем выше значение, тем более случайным будет ответ модели. При значениях температуры больше двух, набор токенов в ответе модели может отличаться избыточной случайностью.
Значение по умолчанию зависит от выбранной модели.

- Максимум токенов (max_tokens, `int`)

Максимальное количество токенов, которые будут использованы для создания ответов.

- *Использовать встроенный HA командный процессор* (process_builtin_sentences, `bool`)

Если включено, все фразы сначала будут отдаваться [встроенному в HA процессору шаблонных фраз](https://www.home-assistant.io/voice_control/builtin_sentences).
Это основное поведение встроенной в Home Assistant диалоговой системы, что позволяет использовать команды вида `включи телевизор в зале`.
Если фраза не может быть распознана встроенным процессором - она будет передана дальше, выбранной языковой модели.

- *Home Assistant API* (llm_hass_api, `select`)

Управление устройствами дома через официальный [LLM API](https://developers.home-assistant.io/docs/ai/) Home Assistant.
При выборе `Assist` модель получает те же инструменты, что и встроенный агент Assist
(включение/выключение устройств, запрос состояния, установка позиции, таймеры и т.д.) через нативный function calling.
Поддерживается для GigaChat, OpenAI и Anyscale. `None` отключает управление домом (обычный чат).

Недоступно для YandexGPT: у него нет нативного function calling, поэтому управление для него
работает через legacy-схему с JSON `function_call` в промпте (в промпт выводятся сущности,
exposed для Assist). При необходимости настройте *Темплейт промпта* под этот режим.

> Сущности должны быть exposed для Assist (Настройки → Устройства и службы →Expose),
> чтобы модель могла ими управлять.

### Вопросы о местоположении

На вопросы вида «Где мой телефон?», «Где Роман?», «Телефон дома?» интеграция отвечает
по данным трекеров (`person` и `device_tracker`), exposed для Assist. Ответ строится на
зонах Home Assistant: если координаты устройства попадают в зону — называется зона
(например «дома»), иначе сообщается расстояние до дома.

Для GigaChat/OpenAI/Anyscale это отдельный инструмент `GetLocation` (нативный вызов),
для YandexGPT — правило `location` в legacy-промпте.

Чтобы работали вопросы о человеке, к соответствующему `person` должен быть привязан
`device_tracker` (Настройки → Люди). Если у сущности нет GPS-координат, используется её
текущее состояние (`home`/`not_home`/имя зоны).

> Обратного геокодинга (адреса по координатам) нет: ядро Home Assistant его не
> предоставляет, а внешний геокодер не добавляется намеренно. Вне зон сообщается только
> расстояние до дома.

Историю сообщений теперь ведёт сам Home Assistant (по conversation_id), старая опция
`chat_history` удалена.

## Использование в качестве диалоговой системы

Создайте и настройте новый голосовой ассистент:

## Известные ограничения

- **Управление шторами/жалюзи нативными инструментами.** В ядре Home Assistant нет
  отдельных LLM-инструментов для домена `cover`, поэтому на нативном пути шторы
  управляются generic-интентами вкл/выкл (в YandexGPT — правилом `open_close`).
  Сопоставление по имени может быть неточным при «шуме» модели.
- **Лёгкие модели.** GigaChat-2 (не Pro/Max) может давать грязные аргументы
  инструментов (неверные зоны, английские имена для русских сущностей) и не выбирать
  нужный интент. GigaChat-2-Pro / GigaChat-2-Max работают заметно надёжнее.
- **Вопросы о местоположении** отвечаются только по зонам Home Assistant, без
  обратного геокодинга. Для «где <человек>» к персоне должен быть привязан
  `device_tracker`.
- **YandexGPT** не умеет нативный function calling: управление и местоположение
  работают через legacy-схему JSON в промпте. Чат на посторонние темы поддерживается,
  но может быть менее связным, чем у нативных движков.
- **Встроенные фразы.** При включённой опции *Обрабатывать встроенные фразы* типовые
  команды обрабатывает встроенный агент HA ещё до обращения к модели.

