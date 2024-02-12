<br />
<div align="center">

  <a href="https://github.com/ai-forever/gigachain">
    <img src="https://raw.githubusercontent.com/gritaro/gigachain/main/static/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h1 align="center">🦜️🔗 GigaChain (GigaChat + LangChain)</h1>
</div>

# Компонент GigaChain для Home Assistant
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Компонент реализует диалоговую систему Home Assistant для использования с языковыми моделями, поддерживаемыми фреймворком GigaChain.
В настоящее время поддерживается только интеграция с LMM <a href="https://developers.sber.ru/docs/ru/gigachat/overview">GigaChat</a> (русскоязычная нейросеть от Сбера)

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

### Авторизация запросов к GigaChat
Для авторизации запросов к GigaChat вам понадобится получить *авторизационные данные* для работы с GigaChat API.

> [!NOTE]
> О том как получить авторизационные данные для доступа к GigaChat читайте в [официальной документации](https://developers.sber.ru/docs/ru/gigachat/api/integration).
> 

<img src="https://raw.githubusercontent.com/gritaro/gigachain/main/static/auth_data.jpeg" alt="Authorization data" width="40%">

### Конфигурация

* Темплейт промпта
* Модель

## Использование в качестве диалоговой системы
Создайте и настройте новый голосовой ассистент:

<img src="https://raw.githubusercontent.com/gritaro/gigachain/main/static/voice-assistant.jpeg" alt="Voice Assistant">
