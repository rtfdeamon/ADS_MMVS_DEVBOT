"""
Обработчик webhook от Tilda для приема данных из форм
"""
import json
import logging
from datetime import datetime
from typing import Dict, Optional, Any
from pathlib import Path
import hashlib
import hmac

from config import (
    DATA_DIR, LOGS_DIR, WEBHOOK_SECRET, ALLOWED_IPS,
    LOG_FORMAT, LOG_FILE
)

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


class TildaWebhookHandler:
    """Класс для обработки webhook от Tilda"""
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.logs_dir = LOGS_DIR
        
        logger.info("TildaWebhookHandler инициализирован")
    
    def verify_webhook(self, data: Dict, signature: Optional[str] = None, 
                     client_ip: Optional[str] = None) -> bool:
        """
        Проверка подлинности webhook
        
        Args:
            data: Данные webhook
            signature: Подпись запроса (если используется)
            client_ip: IP адрес клиента
            
        Returns:
            True если webhook подлинный
        """
        # Проверка IP адреса (если настроен)
        if ALLOWED_IPS and client_ip:
            if client_ip not in ALLOWED_IPS:
                logger.warning(f"Webhook от неразрешенного IP: {client_ip}")
                return False
        
        # Проверка подписи (если настроен секретный ключ)
        if WEBHOOK_SECRET and signature:
            # Tilda обычно не использует подпись, но можно добавить проверку
            # если будет настроена кастомная интеграция
            pass
        
        return True
    
    def parse_form_data(self, request_data: Dict) -> Dict[str, Any]:
        """
        Парсинг данных формы из Tilda
        
        Args:
            request_data: Данные из webhook запроса
            
        Returns:
            Словарь с распарсенными данными формы
        """
        form_data = {
            'timestamp': datetime.now().isoformat(),
            'form_id': request_data.get('formid', ''),
            'form_name': request_data.get('formname', ''),
            'page_id': request_data.get('pageid', ''),
            'page_url': request_data.get('pageurl', ''),
            'fields': {},
            'raw_data': request_data
        }
        
        # Парсинг полей формы
        # Tilda отправляет данные в разных форматах, обрабатываем основные
        if 'fields' in request_data:
            for field in request_data['fields']:
                field_name = field.get('name', '')
                field_value = field.get('value', '')
                form_data['fields'][field_name] = field_value
        
        # Альтернативный формат (если данные приходят напрямую)
        for key, value in request_data.items():
            if key not in ['formid', 'formname', 'pageid', 'pageurl', 'fields']:
                if key.startswith('field_') or key in ['name', 'email', 'phone', 'message', 'task']:
                    form_data['fields'][key] = value
        
        logger.info(f"Данные формы распарсены: {form_data['form_id']}")
        return form_data
    
    def save_form_submission(self, form_data: Dict) -> Path:
        """
        Сохранение данных формы в файл
        
        Args:
            form_data: Данные формы
            
        Returns:
            Путь к сохраненному файлу
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        form_id = form_data.get('form_id', 'unknown')
        filename = f'tilda_form_{form_id}_{timestamp}.json'
        filepath = self.data_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(form_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Данные формы сохранены: {filepath}")
        return filepath
    
    def process_webhook(self, request_data: Dict, signature: Optional[str] = None,
                       client_ip: Optional[str] = None) -> Dict[str, Any]:
        """
        Обработка webhook запроса от Tilda
        
        Args:
            request_data: Данные из запроса
            signature: Подпись запроса
            client_ip: IP адрес клиента
            
        Returns:
            Результат обработки
        """
        try:
            # Проверка подлинности
            if not self.verify_webhook(request_data, signature, client_ip):
                return {
                    'success': False,
                    'error': 'Webhook verification failed'
                }
            
            # Парсинг данных
            form_data = self.parse_form_data(request_data)
            
            # Сохранение данных
            filepath = self.save_form_submission(form_data)
            
            # Возврат результата
            return {
                'success': True,
                'form_id': form_data.get('form_id'),
                'saved_to': str(filepath),
                'data': form_data
            }
            
        except Exception as e:
            logger.error(f"Ошибка при обработке webhook: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_form_statistics(self, days: int = 30) -> Dict:
        """
        Получение статистики по формам за период
        
        Args:
            days: Количество дней для анализа
            
        Returns:
            Статистика по формам
        """
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        stats = {
            'total_submissions': 0,
            'by_form_id': {},
            'by_date': {},
            'fields_summary': {}
        }
        
        # Чтение всех файлов с формами
        for filepath in self.data_dir.glob('tilda_form_*.json'):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                timestamp = datetime.fromisoformat(data.get('timestamp', ''))
                if timestamp < cutoff_date:
                    continue
                
                stats['total_submissions'] += 1
                
                form_id = data.get('form_id', 'unknown')
                stats['by_form_id'][form_id] = stats['by_form_id'].get(form_id, 0) + 1
                
                date_key = timestamp.strftime('%Y-%m-%d')
                stats['by_date'][date_key] = stats['by_date'].get(date_key, 0) + 1
                
                # Анализ полей
                for field_name, field_value in data.get('fields', {}).items():
                    if field_name not in stats['fields_summary']:
                        stats['fields_summary'][field_name] = {
                            'count': 0,
                            'sample_values': []
                        }
                    stats['fields_summary'][field_name]['count'] += 1
                    if len(stats['fields_summary'][field_name]['sample_values']) < 5:
                        stats['fields_summary'][field_name]['sample_values'].append(str(field_value)[:50])
                        
            except Exception as e:
                logger.error(f"Ошибка при чтении файла {filepath}: {e}")
        
        return stats

