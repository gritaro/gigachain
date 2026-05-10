[en](https://github.com/gritaro/gigachain/blob/main/README.md)
[ru](https://github.com/gritaro/gigachain/blob/main/README-ru.md)
  




Исправленная версия с поддержкой 2026.5

# 🦜️🔗 GigaChain (GigaChat + LangChain)

# Компонент GigaChain для Home Assistant

[HACS](https://hacs.xyz)
[HACS Action](https://github.com/gritaro/gigachain/actions/workflows/hacs.yaml)
[Validate with hassfest](https://github.com/gritaro/gigachain/actions/workflows/hassfest.yaml)
[Generic badge](https://github.com/gritaro/gigachain)
[Downloads for latest release](https://github.com/gritaro/gigachain/releases/latest)
[Github All Releases](https://github.com/gritaro/gigachain/releases)

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

- История сообщений (chat_history, `bool`)

Если у вашей модели дорогой тариф, либо ваш сценарий использования это позволяет, вы можете отключить историю. В противном случае вся история диалога передаётся в каждом запросе.

## Использование в качестве диалоговой системы

Создайте и настройте новый голосовой ассистент:

