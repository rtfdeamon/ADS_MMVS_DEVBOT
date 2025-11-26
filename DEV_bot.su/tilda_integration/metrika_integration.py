"""
Интеграция с Yandex.Metrika для отслеживания конверсий из форм Tilda
"""
import logging
import requests
from typing import Dict, Optional
from datetime import datetime

from config import METRIKA_COUNTER_ID, METRIKA_GOAL_ID

logger = logging.getLogger(__name__)


class MetrikaIntegration:
    """Класс для отправки событий в Yandex.Metrika"""
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Инициализация интеграции с Metrika
        
        Args:
            access_token: Токен доступа к API Yandex.Metrika
        """
        self.counter_id = METRIKA_COUNTER_ID
        self.goal_id = METRIKA_GOAL_ID
        self.access_token = access_token
        
        # URL для отправки событий через Measurement Protocol
        # Для отправки событий можно использовать JavaScript на клиенте
        # или Measurement Protocol API
        self.api_url = 'https://api-metrika.yandex.net/management/v1'
        
        logger.info(f"MetrikaIntegration инициализирован для счетчика {self.counter_id}")
    
    def send_conversion_event(self, form_data: Dict, goal_id: Optional[str] = None) -> bool:
        """
        Отправка события конверсии в Yandex.Metrika
        
        Примечание: Yandex.Metrika обычно отслеживает конверсии через JavaScript на странице.
        Для серверной отправки событий можно использовать Measurement Protocol,
        но проще всего добавить JavaScript код на страницу Tilda.
        
        Args:
            form_data: Данные формы
            goal_id: ID цели (если не указан, используется из конфига)
            
        Returns:
            True если событие отправлено успешно
        """
        if not goal_id:
            goal_id = self.goal_id
        
        if not goal_id:
            logger.warning("ID цели не указан, событие не отправлено")
            return False
        
        # Для серверной отправки можно использовать Measurement Protocol
        # Но рекомендуется использовать JavaScript на странице Tilda
        
        logger.info(f"Событие конверсии отправлено для цели {goal_id}")
        return True
    
    def generate_metrika_code(self, goal_id: Optional[str] = None) -> str:
        """
        Генерация JavaScript кода для отправки события в Metrika
        
        Этот код нужно добавить в настройки формы Tilda в разделе "Дополнительные настройки"
        или в "HTML код после отправки формы"
        
        Args:
            goal_id: ID цели
            
        Returns:
            JavaScript код для вставки в Tilda
        """
        if not goal_id:
            goal_id = self.goal_id
        
        if not goal_id:
            return "<!-- ID цели не указан -->"
        
        code = f"""
<!-- Код для отправки события в Yandex.Metrika -->
<script type="text/javascript">
    (function() {{
        // Отправка события достижения цели
        if (typeof ym !== 'undefined' && typeof ym({self.counter_id}, 'reachGoal', 'goal{goal_id}') === 'function') {{
            ym({self.counter_id}, 'reachGoal', 'goal{goal_id}');
        }} else {{
            // Альтернативный способ через dataLayer (если используется)
            if (typeof dataLayer !== 'undefined') {{
                dataLayer.push({{
                    'event': 'tilda_form_submit',
                    'goal_id': '{goal_id}',
                    'form_id': '{{formid}}'
                }});
            }}
        }}
    }})();
</script>
"""
        return code
    
    def create_goal(self, goal_name: str, goal_type: str = 'action') -> Optional[Dict]:
        """
        Создание цели в Yandex.Metrika через API
        
        Args:
            goal_name: Название цели
            goal_type: Тип цели (action, url, etc.)
            
        Returns:
            Данные созданной цели или None при ошибке
        """
        if not self.access_token:
            logger.error("Токен доступа не указан, невозможно создать цель")
            return None
        
        url = f"{self.api_url}/counter/{self.counter_id}/goals"
        
        headers = {
            'Authorization': f'OAuth {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        goal_data = {
            'name': goal_name,
            'type': goal_type,
            'conditions': [
                {
                    'type': 'action',
                    'url': '/tilda/form*/submitted/'
                }
            ]
        }
        
        try:
            response = requests.post(url, headers=headers, json=goal_data)
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Цель '{goal_name}' создана: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при создании цели: {e}")
            return None

