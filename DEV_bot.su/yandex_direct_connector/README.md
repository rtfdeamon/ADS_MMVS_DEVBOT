# Коннектор Яндекс.Директ для DEV_bot

Модуль для работы с API Яндекс.Директ, сбора данных о рекламных кампаниях и анализа стратегии поведения.

## Структура проекта

```
yandex_direct_connector/
├── config.py              # Конфигурация и настройки
├── connector.py            # Основной коннектор для работы с API
├── data_collector.py       # Модуль сбора данных
├── analyzer.py             # Модуль анализа стратегии
├── test_connector.py       # Тестовый скрипт
├── requirements.txt        # Зависимости
├── README.md              # Документация
├── data/                  # Сохраненные данные (создается автоматически)
├── reports/               # Отчеты и анализ (создается автоматически)
└── logs/                  # Логи (создается автоматически)
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

3. Настройте токен доступа:
   - Откройте файл `../config.txt` и убедитесь, что там указан токен Яндекс.Директ
   - Или установите переменную окружения: `export YANDEX_DIRECT_TOKEN=your_token`

## Использование

### Базовое использование

```python
from connector import YandexDirectConnector
from data_collector import DataCollector
from analyzer import StrategyAnalyzer

# Инициализация коннектора
connector = YandexDirectConnector()

# Получение списка кампаний
campaigns = connector.get_campaigns()
print(f"Найдено кампаний: {len(campaigns)}")

# Получение информации о клиенте
client_info = connector.get_client_info()
print(f"Логин клиента: {client_info.get('Login')}")
```

### Сбор данных

```python
# Создание сборщика данных
collector = DataCollector(connector)

# Сбор всех данных
data = collector.collect_all_data()

# Сохранение в JSON
json_file = collector.save_data(data)

# Экспорт в Excel
excel_file = collector.export_to_excel(data)
```

### Анализ стратегии

```python
# Создание анализатора
analyzer = StrategyAnalyzer()

# Выполнение анализа
analysis = analyzer.analyze_campaigns(data)

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
python test_connector.py
```

Скрипт выполнит следующие тесты:
1. Проверка подключения к API
2. Получение списка кампаний
3. Получение групп объявлений
4. Получение объявлений
5. Получение ключевых слов
6. Сбор всех данных
7. Анализ стратегии

## API Методы

### YandexDirectConnector

- `get_campaigns(campaign_ids=None, field_names=None)` - Получение кампаний
- `get_ad_groups(campaign_ids=None, ad_group_ids=None, field_names=None)` - Получение групп объявлений
- `get_ads(campaign_ids=None, ad_group_ids=None, ad_ids=None, field_names=None)` - Получение объявлений
- `get_keywords(campaign_ids=None, ad_group_ids=None, keyword_ids=None, field_names=None)` - Получение ключевых слов
- `get_client_info()` - Получение информации о клиенте

### DataCollector

- `collect_all_data(campaign_ids=None)` - Сбор всех данных
- `save_data(data, filename=None)` - Сохранение данных в JSON
- `load_data(filename)` - Загрузка данных из JSON
- `export_to_excel(data, filename=None)` - Экспорт в Excel
- `get_campaign_structure(campaign_id)` - Получение структуры кампании

### StrategyAnalyzer

- `analyze_campaigns(data)` - Анализ кампаний
- `save_analysis(analysis, filename=None)` - Сохранение анализа
- `export_analysis_report(analysis, filename=None)` - Экспорт отчета в Excel

## Структура данных

### Данные кампании
- ID, название, тип, статус
- Бюджет и стратегия показа
- Даты начала и окончания
- Статистика (если доступна)

### Данные группы объявлений
- ID, название, ID кампании
- Минус-слова
- Статус и статистика

### Данные объявления
- ID, тип, статус
- Текст объявления
- Ставки (CPC, CPM)
- Статистика

### Данные ключевые слова
- ID, ключевое слово
- Ставка, статус
- Статистика по поиску и сети

## Анализ стратегии

Анализатор предоставляет:
- Общую статистику по кампаниям
- Анализ по каждой кампании
- Анализ ключевых слов (топ, распределение ставок)
- Автоматические рекомендации по оптимизации

## Логирование

Все операции логируются в файл `logs/yandex_direct_connector.log` и выводятся в консоль.

## Обработка ошибок

Коннектор автоматически обрабатывает:
- Ошибки сети (retry с экспоненциальной задержкой)
- Ошибки API (логирование и исключения)
- Таймауты запросов

## Получение токена

1. Зайдите в [Яндекс.Директ](https://direct.yandex.ru)
2. Перейдите в раздел "Настройки" → "API"
3. Создайте токен доступа
4. Сохраните токен в `config.txt` или переменную окружения

## Лицензия

Внутренний проект для DEV_bot.

## Поддержка

При возникновении проблем проверьте:
1. Правильность токена
2. Доступность API Яндекс.Директ
3. Логи в файле `logs/yandex_direct_connector.log`

