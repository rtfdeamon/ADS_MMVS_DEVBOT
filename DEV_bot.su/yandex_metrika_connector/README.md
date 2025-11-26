# Коннектор Яндекс.Метрика для DEV_bot

Модуль для работы с API Яндекс.Метрика, сбора данных о счетчиках и анализа метрик.

## Структура проекта

```
yandex_metrika_connector/
├── config.py              # Конфигурация и настройки
├── oauth.py               # OAuth авторизация
├── connector.py            # Основной коннектор для работы с API
├── data_collector.py       # Модуль сбора данных
├── analyzer.py            # Модуль анализа метрик
├── test_connector.py      # Тестовый скрипт
├── requirements.txt       # Зависимости
├── README.md              # Документация
├── data/                 # Сохраненные данные (создается автоматически)
├── reports/              # Отчеты и анализ (создается автоматически)
├── logs/                 # Логи (создается автоматически)
└── tokens/               # Токены доступа (создается автоматически)
```

## Установка

1. Создайте виртуальное окружение (рекомендуется):
```bash
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Авторизация (OAuth)

Перед использованием необходимо получить токен доступа через OAuth:

```bash
python3 oauth.py
```

Скрипт:
1. Откроет браузер с формой авторизации Яндекс
2. После авторизации вы будете перенаправлены на указанный redirect URI
3. Скопируйте код из URL (параметр `code`)
4. Вставьте код в консоль
5. Токен будет сохранен в `tokens/access_token.json`

### Альтернативный способ

Вы можете получить токен вручную:
1. Перейдите по ссылке авторизации (получите через `oauth.py`)
2. Авторизуйтесь в Яндекс
3. Скопируйте код из redirect URL
4. Используйте код для получения токена

## Использование

### Базовое использование

```python
from connector import YandexMetrikaConnector
from data_collector import MetrikaDataCollector
from analyzer import MetrikaAnalyzer

# Инициализация коннектора (токен загружается автоматически)
connector = YandexMetrikaConnector()

# Получение списка счетчиков
counters = connector.get_counters()
print(f"Найдено счетчиков: {len(counters)}")

# Получение информации о счетчике
counter_id = counters[0]['id']
counter_info = connector.get_counter_info(counter_id)
print(f"Сайт: {counter_info.get('site')}")
```

### Сбор данных

```python
# Создание сборщика данных
collector = MetrikaDataCollector(connector)

# Сбор всех данных
data = collector.collect_all_data(counter_id=counter_id)

# Сохранение в JSON
json_file = collector.save_data(data)

# Экспорт в Excel
excel_file = collector.export_to_excel(data)
```

### Анализ данных

```python
# Создание анализатора
analyzer = MetrikaAnalyzer()

# Выполнение анализа
analysis = analyzer.analyze_data(data)

# Просмотр рекомендаций
for recommendation in analysis['recommendations']:
    print(recommendation)

# Сохранение анализа
analyzer.save_analysis(analysis)
analyzer.export_analysis_report(analysis)
```

## Тестирование

Запустите тестовый скрипт для проверки работы коннектора:

```bash
python3 test_connector.py
```

Скрипт выполнит следующие тесты:
1. Проверка OAuth авторизации
2. Проверка подключения к API
3. Получение списка счетчиков
4. Получение информации о счетчике
5. Получение целей
6. Получение отчетов (визиты, источники, страницы, география)
7. Сбор всех данных
8. Анализ данных

## API Методы

### YandexMetrikaConnector

- `get_counters()` - Получение списка счетчиков
- `get_counter_info(counter_id)` - Получение информации о счетчике
- `get_goals(counter_id)` - Получение целей счетчика
- `get_filters(counter_id)` - Получение фильтров счетчика
- `get_visits_report(counter_id, date_from, date_to, ...)` - Отчет о визитах
- `get_sources_report(counter_id, date_from, date_to, ...)` - Отчет по источникам
- `get_pages_report(counter_id, date_from, date_to, ...)` - Отчет по страницам
- `get_geo_report(counter_id, date_from, date_to, ...)` - Отчет по географии

### MetrikaDataCollector

- `collect_all_data(counter_id, date_from, date_to)` - Сбор всех данных
- `save_data(data, filename)` - Сохранение данных в JSON
- `load_data(filename)` - Загрузка данных из JSON
- `export_to_excel(data, filename)` - Экспорт в Excel

### MetrikaAnalyzer

- `analyze_data(data)` - Анализ данных
- `save_analysis(analysis, filename)` - Сохранение анализа
- `export_analysis_report(analysis, filename)` - Экспорт отчета в Excel

## Структура данных

### Данные счетчика
- ID, название, сайт, статус
- Тип счетчика
- Настройки и параметры

### Отчеты
- **Визиты**: визиты, просмотры, пользователи, отказы, глубина просмотра, длительность
- **Источники**: источники трафика, поисковые системы
- **Страницы**: популярные страницы, просмотры по страницам
- **География**: страны, города, распределение трафика

## Анализ данных

Анализатор предоставляет:
- Общую статистику по счетчику
- Анализ трафика (визиты, отказы, глубина просмотра)
- Анализ источников (топ источников, поисковые системы)
- Анализ страниц (топ страниц)
- Анализ географии (топ стран и городов)
- Автоматические рекомендации по оптимизации

## OAuth настройки

В файле `config.py` указаны настройки OAuth:
- `OAUTH_CLIENT_ID` - ID приложения
- `OAUTH_CLIENT_SECRET` - Секретный ключ
- `OAUTH_REDIRECT_URI` - URI для перенаправления

Эти настройки уже заполнены для вашего приложения.

## Логирование

Все операции логируются в файл `logs/yandex_metrika_connector.log` и выводятся в консоль.

## Обработка ошибок

Коннектор автоматически обрабатывает:
- Ошибки сети (retry с экспоненциальной задержкой)
- Ошибки API (логирование и исключения)
- Таймауты запросов
- Проблемы с авторизацией

## Получение OAuth данных

OAuth данные уже настроены в `config.py`:
- ClientID: `87dd75faf38d40d6afb0a9a9e2a29706`
- Client Secret: `db00b07c5c804a4691a3a67b7b4c09c2`
- Redirect URI: `https://mmvs.ru/metrika`

## Лицензия

Внутренний проект для DEV_bot.

## Поддержка

При возникновении проблем проверьте:
1. Правильность OAuth данных
2. Наличие токена доступа
3. Доступность API Яндекс.Метрика
4. Логи в файле `logs/yandex_metrika_connector.log`

