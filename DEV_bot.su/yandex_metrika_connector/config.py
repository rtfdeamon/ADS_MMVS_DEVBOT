"""
Конфигурация для коннектора Яндекс.Метрика
"""
import os
from pathlib import Path

# Путь к корневой директории проекта
BASE_DIR = Path(__file__).parent.parent

# OAuth настройки
OAUTH_CLIENT_ID = '87dd75faf38d40d6afb0a9a9e2a29706'
OAUTH_CLIENT_SECRET = 'db00b07c5c804a4691a3a67b7b4c09c2'
OAUTH_REDIRECT_URI = 'https://mmvs.ru/metrika'

# URL для OAuth
OAUTH_AUTHORIZE_URL = 'https://oauth.yandex.ru/authorize'
OAUTH_TOKEN_URL = 'https://oauth.yandex.ru/token'

# URL API Яндекс.Метрика
API_URL = 'https://api-metrika.yandex.net/management/v1'
REPORTING_API_URL = 'https://api-metrika.yandex.net/stat/v1'

# Токен доступа (будет получен через OAuth)
ACCESS_TOKEN = os.getenv('YANDEX_METRIKA_TOKEN', '')

# Настройки для запросов
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3

# Папки для сохранения данных
DATA_DIR = BASE_DIR / 'yandex_metrika_connector' / 'data'
REPORTS_DIR = BASE_DIR / 'yandex_metrika_connector' / 'reports'
LOGS_DIR = BASE_DIR / 'yandex_metrika_connector' / 'logs'
TOKENS_DIR = BASE_DIR / 'yandex_metrika_connector' / 'tokens'

# Создаем необходимые директории
for directory in [DATA_DIR, REPORTS_DIR, LOGS_DIR, TOKENS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Настройки логирования
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = LOGS_DIR / 'yandex_metrika_connector.log'

# Настройки по умолчанию для отчетов
DEFAULT_METRICS = [
    'ym:s:visits',
    'ym:s:pageviews',
    'ym:s:users',
    'ym:s:bounceRate',
    'ym:s:pageDepth',
    'ym:s:avgVisitDurationSeconds'
]

DEFAULT_DIMENSIONS = [
    'ym:s:date',
    'ym:s:trafficSource',
    'ym:s:searchEngine',
    'ym:s:referer'
]

