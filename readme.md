# 

Чат бот для telegram для интеграции с [https://github.com/AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui)

Переменные окружения для настройки бота 

TOKEN= telegram token
DSN= dsn glitchtip или sentry
API_HOST= хост где запущен https://github.com/AUTOMATIC1111/stable-diffusion-webui
API_PORT=порт где запущен https://github.com/AUTOMATIC1111/stable-diffusion-webui
ADMIN_CHAT_ID= идентификатор чата админа, чтобы все запросы дублировались для отладки

# Чат-бот для Telegram для интеграции с Stable Diffusion WebUI

Этот чат-бот позволяет интегрировать Telegram с [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui), чтобы вы могли генерировать картинки в Telegram.

## Переменные окружения

Перед запуском чат-бота, вы должны настроить следующие переменные окружения:

- `TOKEN` - токен Telegram
- `DSN` - DSN для [Glitchtip](https://github.com/glitchtip/glitchtip) или [Sentry](https://sentry.io/)
- `API_HOST` - хост, где запущен Stable Diffusion WebUI
- `API_PORT` - порт, на котором запущен Stable Diffusion WebUI
- `ADMIN_CHAT_ID` - идентификатор чата админа, чтобы все запросы дублировались для отладки

## Использование

Чтобы использовать этот чат-бот, просто напишите боту в Telegram.

## Вопросы и отладка

Если у вас есть какие-либо вопросы или проблемы с этим чат-ботом, напишите в https://github.com/vpuhoff/sd-telegram-bot/issues.

## Как запустить чат-бота

Чтобы запустить этот чат-бот, вам нужно сначала установить его на вашем сервере. Затем вы должны настроить переменные окружения, перечисленные выше.

После того, как вы настроили переменные окружения, вы можете запустить чат-бота, выполнив следующую команду:

```
python main.py

```

Если вы хотите запустить чат-бота в фоновом режиме, вы можете использовать [Supervisor](http://supervisord.org/) или [systemd](https://www.freedesktop.org/software/systemd/man/systemd.service.html).

## Как настроить Glitchtip или Sentry

Если вы хотите использовать Glitchtip или Sentry для отслеживания ошибок в этом чат-боте, вы должны сначала создать новый проект в Glitchtip или Sentry.

Затем вы должны настроить переменную окружения `DSN`, чтобы указать на DSN вашего проекта.

После того, как вы настроили DSN, вы можете отправлять ошибки и события в Glitchtip или Sentry.