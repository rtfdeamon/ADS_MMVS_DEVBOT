"""
Конфигурация для коннектора Яндекс.Директ
"""
import os
from pathlib import Path

# Путь к корневой директории проекта
BASE_DIR = Path(__file__).parent.parent

# Чтение токена из config.txt
CONFIG_FILE = BASE_DIR / 'config.txt'
YANDEX_DIRECT_TOKEN = None

if CONFIG_FILE.exists():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Yandex.Direct API token:' in line:
                YANDEX_DIRECT_TOKEN = line.split(':', 1)[1].strip()
                break

# Если токен не найден в файле, попробуем из переменной окружения
if not YANDEX_DIRECT_TOKEN:
    YANDEX_DIRECT_TOKEN = os.getenv('YANDEX_DIRECT_TOKEN', '')

# URL API Яндекс.Директ
API_URL = 'https://api.direct.yandex.com/json/v5'

# Настройки по умолчанию
DEFAULT_CLIENT_LOGIN = os.getenv('YANDEX_DIRECT_CLIENT_LOGIN', '')
DEFAULT_LANGUAGE = 'ru'  # ru, en, uk, tr

# Настройки для запросов
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3

# Папки для сохранения данных
DATA_DIR = BASE_DIR / 'yandex_direct_connector' / 'data'
REPORTS_DIR = BASE_DIR / 'yandex_direct_connector' / 'reports'
LOGS_DIR = BASE_DIR / 'yandex_direct_connector' / 'logs'

# Создаем необходимые директории
for directory in [DATA_DIR, REPORTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Настройки логирования
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = LOGS_DIR / 'yandex_direct_connector.log'

