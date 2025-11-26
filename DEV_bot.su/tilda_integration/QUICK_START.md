# Быстрый старт: Интеграция с Tilda

## Шаг 1: Установка зависимостей

```bash
cd tilda_integration
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Шаг 2: Настройка переменных окружения

Создайте файл `.env` или экспортируйте переменные:

```bash
# Yandex.Metrika
export METRIKA_COUNTER_ID="101775445"  # ID счетчика dev-bot.su
export METRIKA_GOAL_ID="your_goal_id"   # ID цели (создайте в Metrika)

# Telegram уведомления (опционально)
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# Email уведомления (опционально)
export EMAIL_NOTIFICATIONS="rtfdeamon@yandex.ru"
```

## Шаг 3: Запуск сервера

### Локально (для тестирования):
```bash
python3 main.py
```

Сервер будет доступен на `http://localhost:5000`

### Для продакшена:
Используйте gunicorn или разверните на сервере с HTTPS.

## Шаг 4: Настройка webhook в Tilda

1. Войдите в админ-панель Tilda
2. Откройте настройки вашей формы
3. Перейдите в **"Дополнительные настройки"** → **"Webhook"**
4. Укажите URL: `https://your-domain.com/webhook/tilda`
   - Для локального тестирования можно использовать [ngrok](https://ngrok.com/): `ngrok http 5000`
5. Сохраните настройки

## Шаг 5: Настройка отслеживания конверсий

### Вариант A: JavaScript код в Tilda (рекомендуется)

1. Получите код:
```bash
curl http://localhost:5000/webhook/tilda/metrika-code?goal_id=YOUR_GOAL_ID
```

2. В Tilda:
   - Настройки формы → **"HTML код после отправки формы"**
   - Вставьте полученный код
   - Сохраните

### Вариант B: Создание цели через API

```python
from metrika_integration import MetrikaIntegration

# Используйте токен из yandex_metrika_connector
metrika = MetrikaIntegration(access_token='your_token')
goal = metrika.create_goal('Заявка с формы Tilda', 'action')
```

## Шаг 6: Тестирование

Отправьте тестовую форму на вашем сайте Tilda и проверьте:

1. **Логи**: `logs/tilda_integration.log`
2. **Сохраненные данные**: `data/tilda_form_*.json`
3. **Статистика**: `curl http://localhost:5000/webhook/tilda/stats`

## Проверка работы

```bash
# Проверка здоровья сервиса
curl http://localhost:5000/webhook/tilda/health

# Получение статистики
curl http://localhost:5000/webhook/tilda/stats?days=7
```

## Структура данных

Все заявки автоматически сохраняются в `data/` в формате:
```json
{
  "timestamp": "2025-11-24T12:00:00",
  "form_id": "1023590156",
  "form_name": "Консультация",
  "page_url": "https://dev-bot.su/",
  "fields": {
    "name": "Иван Иванов",
    "email": "ivan@example.com",
    "phone": "+79001234567"
  }
}
```

## Что дальше?

- Настройте уведомления в Telegram
- Интегрируйте с вашей CRM системой
- Настройте автоматическую отправку писем клиентам
- Добавьте аналитику по источникам трафика

Подробная документация: см. `README.md`

