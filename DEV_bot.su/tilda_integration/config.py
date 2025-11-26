"""
Конфигурация для интеграции с Tilda
"""
import os
from pathlib import Path

# Путь к корневой директории проекта
BASE_DIR = Path(__file__).parent.parent

# Настройки для сохранения данных
DATA_DIR = BASE_DIR / 'tilda_integration' / 'data'
LOGS_DIR = BASE_DIR / 'tilda_integration' / 'logs'
REPORTS_DIR = BASE_DIR / 'tilda_integration' / 'reports'

# Создаем необходимые директории
for directory in [DATA_DIR, LOGS_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Настройки логирования
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = LOGS_DIR / 'tilda_integration.log'

# Настройки для Yandex.Metrika
METRIKA_COUNTER_ID = os.getenv('METRIKA_COUNTER_ID', '101775445')  # ID счетчика dev-bot.su
METRIKA_GOAL_ID = os.getenv('METRIKA_GOAL_ID', '')  # ID цели для отслеживания заявок

# Настройки для уведомлений
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
EMAIL_NOTIFICATIONS = os.getenv('EMAIL_NOTIFICATIONS', 'rtfdeamon@yandex.ru')

# Настройки безопасности
WEBHOOK_SECRET = os.getenv('TILDA_WEBHOOK_SECRET', '')  # Секретный ключ для проверки webhook
ALLOWED_IPS = os.getenv('TILDA_ALLOWED_IPS', '').split(',') if os.getenv('TILDA_ALLOWED_IPS') else []

# Настройки для API Tilda (если нужно)
TILDA_API_KEY = os.getenv('TILDA_API_KEY', '')
TILDA_API_SECRET = os.getenv('TILDA_API_SECRET', '')

