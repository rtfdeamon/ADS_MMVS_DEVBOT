# Интеграция с Tilda

Модуль для интеграции форм Tilda с системой обработки заявок, отслеживания конверсий в Yandex.Metrika и отправки уведомлений.

## Возможности

- ✅ Прием webhook от Tilda при отправке форм
- ✅ Сохранение всех заявок в структурированном виде
- ✅ Отслеживание конверсий в Yandex.Metrika
- ✅ Уведомления в Telegram и Email
- ✅ Статистика по формам и заявкам
- ✅ Генерация JavaScript кода для отслеживания целей

## Установка

1. Установите зависимости:
```bash
cd tilda_integration
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Настройте переменные окружения (создайте файл `.env` или экспортируйте переменные):
```bash
export METRIKA_COUNTER_ID="101775445"
export METRIKA_GOAL_ID="your_goal_id"
export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
export TELEGRAM_CHAT_ID="your_telegram_chat_id"
export EMAIL_NOTIFICATIONS="your_email@example.com"
```

## Использование

### 1. Настройка webhook в Tilda

1. Войдите в админ-панель Tilda
2. Откройте настройки формы
3. Перейдите в раздел "Дополнительные настройки" → "Webhook"
4. Укажите URL вашего сервера: `https://your-domain.com/webhook/tilda`
5. Сохраните настройки

### 2. Запуск сервера

#### Локальная разработка:
```bash
python3 main.py
```

#### Продакшен (с gunicorn):
```bash
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### 3. Настройка отслеживания конверсий в Yandex.Metrika

#### Вариант 1: JavaScript код на странице Tilda

1. Получите код для вставки:
```bash
curl http://localhost:5000/webhook/tilda/metrika-code?goal_id=YOUR_GOAL_ID
```

2. В Tilda:
   - Откройте настройки формы
   - Перейдите в "HTML код после отправки формы"
   - Вставьте полученный код
   - Сохраните

#### Вариант 2: Создание цели через API

```python
from metrika_integration import MetrikaIntegration

metrika = MetrikaIntegration(access_token='your_token')
goal = metrika.create_goal('Заявка с формы Tilda', 'action')
```

### 4. Настройка уведомлений

#### Telegram уведомления:

1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Получите токен бота
3. Узнайте ваш chat_id (можно через [@userinfobot](https://t.me/userinfobot))
4. Установите переменные окружения:
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

#### Email уведомления:

Настройте SMTP сервер в файле `notifications.py` или используйте сервис типа SendGrid/Mailgun.

## API Endpoints

### POST/GET `/webhook/tilda`
Основной endpoint для приема webhook от Tilda.

**Пример запроса:**
```json
{
  "formid": "1023590156",
  "formname": "Консультация",
  "pageid": "12345",
  "pageurl": "https://dev-bot.su/",
  "fields": [
    {"name": "name", "value": "Иван Иванов"},
    {"name": "email", "value": "ivan@example.com"},
    {"name": "phone", "value": "+79001234567"}
  ]
}
```

### GET `/webhook/tilda/health`
Проверка работоспособности сервиса.

### GET `/webhook/tilda/stats?days=30`
Получение статистики по формам за указанный период.

### GET `/webhook/tilda/metrika-code?goal_id=123`
Получение JavaScript кода для отслеживания целей в Yandex.Metrika.

## Структура данных

Все заявки сохраняются в папке `data/` в формате JSON:

```json
{
  "timestamp": "2025-11-24T12:00:00",
  "form_id": "1023590156",
  "form_name": "Консультация",
  "page_id": "12345",
  "page_url": "https://dev-bot.su/",
  "fields": {
    "name": "Иван Иванов",
    "email": "ivan@example.com",
    "phone": "+79001234567"
  }
}
```

## Примеры использования

### Получение статистики через Python:

```python
from webhook_handler import TildaWebhookHandler

handler = TildaWebhookHandler()
stats = handler.get_form_statistics(days=30)
print(f"Всего заявок: {stats['total_submissions']}")
```

### Обработка данных формы:

```python
from webhook_handler import TildaWebhookHandler

handler = TildaWebhookHandler()
result = handler.process_webhook({
    'formid': '1023590156',
    'fields': [
        {'name': 'name', 'value': 'Иван'},
        {'name': 'email', 'value': 'ivan@example.com'}
    ]
})

if result['success']:
    print(f"Заявка сохранена: {result['saved_to']}")
```

## Безопасность

- Проверка IP адресов (настройте `TILDA_ALLOWED_IPS`)
- Использование HTTPS для webhook
- Валидация данных формы
- Логирование всех запросов

## Мониторинг

Все логи сохраняются в `logs/tilda_integration.log`

## Дополнительные возможности

- Интеграция с CRM системами
- Автоматическая отправка писем клиентам
- Аналитика по источникам трафика
- A/B тестирование форм

## Поддержка

При возникновении проблем проверьте:
1. Логи в `logs/tilda_integration.log`
2. Настройки переменных окружения
3. Доступность сервера для Tilda
4. Правильность URL webhook в настройках Tilda

