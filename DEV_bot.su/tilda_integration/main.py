"""
Основной модуль для обработки webhook от Tilda
Можно использовать как Flask/FastAPI приложение или как standalone скрипт
"""
import json
import logging
from typing import Dict, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS

from webhook_handler import TildaWebhookHandler
from metrika_integration import MetrikaIntegration
from notifications import NotificationService
from config import LOG_FORMAT, LOG_FILE

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация Flask приложения
app = Flask(__name__)
CORS(app)  # Разрешаем CORS для запросов от Tilda

# Инициализация обработчиков
webhook_handler = TildaWebhookHandler()
metrika = MetrikaIntegration()
notifications = NotificationService()


@app.route('/webhook/tilda', methods=['POST', 'GET'])
def tilda_webhook():
    """
    Endpoint для приема webhook от Tilda
    
    Tilda может отправлять данные как POST (JSON) или GET (query params)
    """
    try:
        # Получение данных в зависимости от метода
        if request.method == 'POST':
            if request.is_json:
                request_data = request.json
            else:
                request_data = request.form.to_dict()
        else:
            request_data = request.args.to_dict()
        
        # Получение IP адреса клиента
        client_ip = request.remote_addr
        if request.headers.get('X-Forwarded-For'):
            client_ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        
        logger.info(f"Получен webhook от Tilda: {request.method}, IP: {client_ip}")
        
        # Обработка webhook
        result = webhook_handler.process_webhook(
            request_data,
            client_ip=client_ip
        )
        
        if result.get('success'):
            form_data = result.get('data', {})
            
            # Отправка события в Metrika
            metrika.send_conversion_event(form_data)
            
            # Отправка уведомлений
            notification_results = notifications.send_notification(form_data)
            result['notifications'] = notification_results
            
            logger.info(f"Webhook обработан успешно: {result.get('form_id')}")
        else:
            logger.error(f"Ошибка обработки webhook: {result.get('error')}")
        
        return jsonify(result), 200 if result.get('success') else 400
        
    except Exception as e:
        logger.error(f"Критическая ошибка при обработке webhook: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/webhook/tilda/health', methods=['GET'])
def health_check():
    """Проверка работоспособности сервиса"""
    return jsonify({
        'status': 'ok',
        'service': 'tilda_integration'
    }), 200


@app.route('/webhook/tilda/stats', methods=['GET'])
def get_stats():
    """Получение статистики по формам"""
    try:
        days = int(request.args.get('days', 30))
        stats = webhook_handler.get_form_statistics(days)
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/webhook/tilda/metrika-code', methods=['GET'])
def get_metrika_code():
    """Получение JavaScript кода для вставки в Tilda"""
    goal_id = request.args.get('goal_id')
    code = metrika.generate_metrika_code(goal_id)
    return code, 200, {'Content-Type': 'text/html; charset=utf-8'}


if __name__ == '__main__':
    # Запуск Flask сервера
    # Для продакшена используйте gunicorn или uwsgi
    logger.info("Запуск сервера для обработки webhook от Tilda...")
    app.run(host='0.0.0.0', port=5000, debug=True)

