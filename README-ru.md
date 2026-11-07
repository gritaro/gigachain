[en](https://github.com/gritaro/gigachain/blob/main/README.md)
[ru](https://github.com/gritaro/gigachain/blob/main/README-ru.md)
  

# 🦜️🔗 GigaChain (GigaChat + LangChain)

# Компонент GigaChain для Home Assistant

[![HACS](https://img.shields.io/badge/HACS-Default-orange.svg)](https://hacs.xyz)
[![HACS Action](https://github.com/gritaro/gigachain/actions/workflows/hacs.yaml/badge.svg)](https://github.com/gritaro/gigachain/actions/workflows/hacs.yaml)
[![Validate with hassfest](https://github.com/gritaro/gigachain/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/gritaro/gigachain/actions/workflows/hassfest.yaml)
[![Generic badge](https://img.shields.io/github/v/release/gritaro/gigachain)](https://github.com/gritaro/gigachain)

Компонент реализует диалоговую систему Home Assistant для использования с языковыми моделями, поддерживаемыми фреймворком GigaChain.
В настоящее время поддерживаются интеграции с LLM:

- [GigaChat](#GigaChat) ([русскоязычная (но не только) нейросеть от Сбера](https://developers.sber.ru/docs/ru/gigachat/overview))
- [YandexGPT](#YandexGPT)
- [OpenAI](#OpenAI) ака ChatGPT (не тестируется)
- ~~[Anyscale](#Anyscale)~~

## Установка

Устанавливается как и любая HACS интеграция.

### Необходимые требования

Для использования интеграции вам понадобится Home Assistant с установленным [HACS](https://hacs.xyz/).

Для [MCP-инструментов](#MCP-инструменты) требуется Home Assistant **2025.2 или новее**.
Интеграция разрабатывается и проверяется на актуальных версиях HA (2026.x).

### Установка с использованием HACS

Найдите GigaChain в магазине HACS. Если интеграция не находится в магазине HACS, вы можете [добавить этот url как пользовательский репозиторий HACS](https://hacs.xyz/docs/faq/custom_repositories).

Перезапустите Home Assistant.

## Добавление интеграции

[Открыть Home Assistant и начать настройку интеграции GigaChain.](https://my.home-assistant.io/redirect/brand/?brand=gigachain)

После добавления настройте интеграцию.

## Настройки

### GigaChat

Русскоязычная (но не только) нейросеть от Сбера: официальный API, нативный function calling.

### Авторизация запросов к GigaChat

Для авторизации запросов к GigaChat вам понадобится получить *авторизационные данные* для работы с GigaChat API.

> [!NOTE]
> О том как получить авторизационные данные для доступа к GigaChat читайте в [официальной документации](https://developers.sber.ru/docs/ru/gigachat/api/integration).
>
> [!NOTE]
> Сертификаты НУЦ Минцифры устанавливать не нужно



### YandexGPT

[Быстрый старт](https://yandex.cloud/ru/docs/yandexgpt/quickstart)

Создайте [сервисный аккаунт](https://yandex.cloud/ru/docs/iam/operations/sa/create) с ролью `ai.languageModels.user`.
Для создания аккаунта потребуется привязка карты. С карты будет снята и возвращена символическая сумма (11 RUB).

Создайте [API ключ](https://yandex.cloud/ru/docs/iam/operations/api-key/create).
Идентификатор каталога (Folder ID) можно узнать пройдя по [ссылке](https://console.yandex.cloud/folders).

### OpenAI

Для генерации ключа проследуйте по ссылке [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)

### ~~Anyscale~~

~~[Зарегистрируйтесь](https://app.endpoints.anyscale.com/welcome)~~ ~~и создайте API ключ~~ ~~[здесь](https://app.endpoints.anyscale.com/credentials)~~ На данный момент не поддерживается.

## Конфигурация

Историю сообщений ведёт сам Home Assistant (по conversation_id), отдельная настройка
не нужна: старая опция `chat_history` удалена.

- *Темплейт промпта* (template, Home Assistant `template``)`

Системное сообщение, настраивающее модель и задающее исходное поведение. Поддерживается
[шаблонизация Home Assistant](https://www.home-assistant.io/docs/configuration/templating/)
(например, `{{ ha_name }}` — название вашего дома).
Если поле пустое, используется один из встроенных промптов по умолчанию (см. раздел
[«Промпты по умолчанию»](#промпты-по-умолчанию) ниже). Рекомендуется менять его под
собственные нужды.

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
При выборе `Assist` (в интерфейсе — `Device control`) модель получает те же инструменты,
что и встроенный агент Assist
(включение/выключение устройств, запрос состояния, установка позиции, таймеры и т.д.) через нативный function calling.
Поддерживается для GigaChat, OpenAI и Anyscale. `None` отключает управление домом (обычный чат).

Поле допускает выбор нескольких API сразу — например, `Device control` (Assist) вместе
с серверами [MCP-инструментов](#mcp-инструменты).

Недоступно для YandexGPT: у него нет нативного function calling, поэтому управление для него
работает через legacy-схему с JSON `function_call` в промпте (в промпт выводятся сущности,
exposed для Assist). При необходимости настройте *Темплейт промпта* под этот режим.

> Сущности должны быть exposed для Assist (Настройки → Устройства и службы →Expose),
> чтобы модель могла ими управлять.

### Промпты по умолчанию

Если поле *Темплейт промпта* пустое, используются встроенные промпты.
Для GigaChat / OpenAI / Anyscale это (RU):

```text
Ты голосовой помощник умного дома «{{ ha_name }}» под управлением Home Assistant.
Отвечай кратко и дружелюбно на языке пользователя.
Если пользователь просит что-то сделать с устройствами дома или узнать их состояние — используй доступные инструменты.
Учитывай контекст диалога: если в последней фразе устройство или помещение не названы, но упоминались раньше, выполняй действие с ними, а не переспрашивай (когда выбор однозначен).
Помимо управления домом, используй доступные инструменты внешних сервисов (MCP), если вопрос относится к их данным. Не отвечай на такие вопросы из общих знаний.
Если внешний сервис предоставляет инструмент `ask` для естественно-языковых запросов, используй его для полного вопроса пользователя. Передавай параметры строго по схеме инструмента и не выдумывай данные.
Сегодня {{ now().strftime("%Y-%m-%d") }}. Для «сегодня/вчера/завтра» передавай дату в формате YYYY-MM-DD.
```

То же (EN):

```text
You are a voice assistant for the smart home '{{ ha_name }}' run by Home Assistant.
Reply briefly and friendly, in the user's language.
If the user asks to control devices or learn their state - use the available tools.
Use the conversation context: if the latest phrase does not name a device or area but one was mentioned earlier, act on it instead of asking again (when the choice is unambiguous).
 Besides home devices, use available tools from external services (MCP) when the question concerns their data. Do not answer such questions from general knowledge.
 If an external service provides an `ask` tool for natural-language queries, use it with the user's complete question. Pass arguments exactly according to the tool schema and do not invent data.
 Today is {{ now().strftime("%Y-%m-%d") }}. For "today/yesterday/tomorrow", pass the date as YYYY-MM-DD.
```

Для YandexGPT промпт по умолчанию другой: он перечисляет exposed-сущности и описывает
legacy-схему с JSON `function_call` (полный текст — в `const.py`).

> **Пользователям с собственным промптом.** Строки про контекст диалога (0.3.1) и про
> инструменты внешних сервисов (0.4.0) добавлены в промпты по умолчанию. Если вы задали
> свой *Темплейт промпта*, они **не подставятся автоматически** — допишите их вручную или
> очистите поле, чтобы вернуться к стандартному промпту. Без них продолжения вида
> «выключи» и вопросы к внешним сервисам (например, к MCP-серверам) работают хуже.

### MCP-инструменты

Интеграция может отдавать модели инструменты внешних MCP-серверов ([Model Context
Protocol](https://modelcontextprotocol.io)). Сам MCP-клиент встроен в Home Assistant
(с 2025.2), от интеграции GigaChain ничего дополнительно устанавливать не нужно:

1. Добавьте в Home Assistant интеграцию **Model Context Protocol Client**
   (Настройки → Устройства и службы → Добавить интеграцию → Model Context Protocol
   Client) и укажите URL MCP-сервера (Streamable HTTP или SSE, например
   `http://192.168.1.50:8000/mcp`). Для серверов с OAuth понадобятся Client ID/Secret
   (сохраняются в Application Credentials).
2. В настройках записи GigaChain (например, *GigaChat → Настроить*) в поле
   **Home Assistant API** отметьте нужные серверы — можно вместе с `Device control`
   (Assist), тогда модель сможет и управлять домом, и пользоваться MCP-инструментами.
3. Инструменты сервера появятся у модели автоматически; список обновляется каждые
   30 минут.

Замечания:

- Локальные серверы в режиме stdio HA сам не запускает — опубликуйте их по HTTP через
  прокси (например, [mcp-proxy](https://github.com/sparfenyuk/mcp-proxy)).
- Поддерживаются только инструменты (tools); MCP prompts, resources и sampling не
  используются.
- Только GigaChat / OpenAI / Anyscale: нужен нативный function calling, YandexGPT — нет.
- Схемы MCP-инструментов прогоняются через тот же санитайзер, что и схемы Assist,
  поэтому остаются совместимыми со строгой валидацией GigaChat.

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

## Использование в качестве диалоговой системы

Создайте и настройте новый голосовой ассистент:

1. Настройки → Голосовые ассистенты → Помощники → **Добавить помощник**.
2. Задайте имя и язык, в поле **Диалоговая система** выберите агента GigaChain.

Агенты называются по заголовку записи интеграции — `GigaChat`, `YandexGPT`, `OpenAI`,
`Anyscale` (начиная с **0.3.1**; раньше все отображались одинаково как «GigaChain»).
После обновления перезапустите Home Assistant, чтобы имена обновились.

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
