"""
Основной коннектор для работы с API Яндекс.Метрика
"""
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import (
    API_URL,
    REPORTING_API_URL,
    ACCESS_TOKEN,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    LOG_FORMAT,
    LOG_FILE
)
from oauth import YandexMetrikaOAuth

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


class YandexMetrikaConnector:
    """Класс для работы с API Яндекс.Метрика"""
    
    def __init__(self, token: Optional[str] = None):
        """
        Инициализация коннектора
        
        Args:
            token: Токен доступа. Если не указан, пытается загрузить из файла или config
        """
        if not token:
            # Пытаемся загрузить токен через OAuth
            oauth = YandexMetrikaOAuth()
            token = oauth.get_valid_token() or ACCESS_TOKEN
        
        if not token:
            raise ValueError(
                "Токен Яндекс.Метрика не найден! "
                "Запустите oauth.py для авторизации или укажите токен в переменной окружения YANDEX_METRIKA_TOKEN"
            )
        
        self.token = token
        
        # Настройка сессии с retry
        self.session = requests.Session()
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        
        logger.info("Коннектор Яндекс.Метрика инициализирован")
    
    def _make_request(self, url: str, params: Optional[Dict] = None, 
                     method: str = 'GET') -> Dict[str, Any]:
        """
        Выполнение запроса к API
        
        Args:
            url: URL запроса
            params: Параметры запроса
            method: HTTP метод
            
        Returns:
            Ответ от API
        """
        headers = {
            'Authorization': f'OAuth {self.token}',
            'Content-Type': 'application/json'
        }
        
        try:
            if method == 'GET':
                response = self.session.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=REQUEST_TIMEOUT
                )
            else:
                response = self.session.post(
                    url,
                    headers=headers,
                    json=params,
                    timeout=REQUEST_TIMEOUT
                )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    logger.error(f"Детали ошибки: {error_data}")
                except:
                    logger.error(f"Ответ сервера: {e.response.text}")
            raise
    
    def get_counters(self) -> List[Dict]:
        """
        Получение списка счетчиков (сайтов)
        
        Returns:
            Список счетчиков
        """
        url = f"{API_URL}/counters"
        
        result = self._make_request(url)
        counters = result.get('counters', [])
        
        logger.info(f"Получено счетчиков: {len(counters)}")
        return counters
    
    def get_counter_info(self, counter_id: int) -> Dict:
        """
        Получение информации о счетчике
        
        Args:
            counter_id: ID счетчика
            
        Returns:
            Информация о счетчике
        """
        url = f"{API_URL}/counter/{counter_id}"
        
        result = self._make_request(url)
        counter = result.get('counter', {})
        
        logger.info(f"Информация о счетчике {counter_id} получена")
        return counter
    
    def get_goals(self, counter_id: int) -> List[Dict]:
        """
        Получение списка целей счетчика
        
        Args:
            counter_id: ID счетчика
            
        Returns:
            Список целей
        """
        url = f"{API_URL}/counter/{counter_id}/goals"
        
        result = self._make_request(url)
        goals = result.get('goals', [])
        
        logger.info(f"Получено целей для счетчика {counter_id}: {len(goals)}")
        return goals
    
    def get_filters(self, counter_id: int) -> List[Dict]:
        """
        Получение списка фильтров счетчика
        
        Args:
            counter_id: ID счетчика
            
        Returns:
            Список фильтров
        """
        url = f"{API_URL}/counter/{counter_id}/filters"
        
        result = self._make_request(url)
        filters = result.get('filters', [])
        
        logger.info(f"Получено фильтров для счетчика {counter_id}: {len(filters)}")
        return filters
    
    def get_visits_report(self, counter_id: int,
                         date_from: Optional[str] = None,
                         date_to: Optional[str] = None,
                         metrics: Optional[List[str]] = None,
                         dimensions: Optional[List[str]] = None,
                         filters: Optional[str] = None,
                         limit: int = 10000) -> Dict:
        """
        Получение отчета о визитах
        
        Args:
            counter_id: ID счетчика
            date_from: Дата начала (YYYY-MM-DD)
            date_to: Дата окончания (YYYY-MM-DD)
            metrics: Список метрик
            dimensions: Список измерений
            filters: Фильтры в формате API
            limit: Лимит строк
            
        Returns:
            Отчет о визитах
        """
        if not date_from:
            date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        if not date_to:
            date_to = datetime.now().strftime('%Y-%m-%d')
        
        if not metrics:
            metrics = [
                'ym:s:visits',
                'ym:s:pageviews',
                'ym:s:users',
                'ym:s:bounceRate',
                'ym:s:pageDepth',
                'ym:s:avgVisitDurationSeconds'
            ]
        
        if not dimensions:
            dimensions = ['ym:s:date']
        
        url = f"{REPORTING_API_URL}/data"
        
        params = {
            'ids': counter_id,
            'date1': date_from,
            'date2': date_to,
            'metrics': ','.join(metrics),
            'dimensions': ','.join(dimensions),
            'limit': limit
        }
        
        if filters:
            params['filters'] = filters
        
        result = self._make_request(url, params=params)
        
        logger.info(f"Отчет о визитах получен для счетчика {counter_id}")
        return result
    
    def get_sources_report(self, counter_id: int,
                          date_from: Optional[str] = None,
                          date_to: Optional[str] = None,
                          limit: int = 100) -> Dict:
        """
        Получение отчета по источникам трафика
        
        Args:
            counter_id: ID счетчика
            date_from: Дата начала
            date_to: Дата окончания
            limit: Лимит строк
            
        Returns:
            Отчет по источникам
        """
        if not date_from:
            date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        if not date_to:
            date_to = datetime.now().strftime('%Y-%m-%d')
        
        url = f"{REPORTING_API_URL}/data"
        
        params = {
            'ids': counter_id,
            'date1': date_from,
            'date2': date_to,
            'metrics': 'ym:s:visits,ym:s:pageviews,ym:s:users',
            'dimensions': 'ym:s:trafficSource,ym:s:sourceEngine',
            'limit': limit
        }
        
        result = self._make_request(url, params=params)
        
        logger.info(f"Отчет по источникам получен для счетчика {counter_id}")
        return result
    
    def get_pages_report(self, counter_id: int,
                        date_from: Optional[str] = None,
                        date_to: Optional[str] = None,
                        limit: int = 100) -> Dict:
        """
        Получение отчета по страницам
        
        Args:
            counter_id: ID счетчика
            date_from: Дата начала
            date_to: Дата окончания
            limit: Лимит строк
            
        Returns:
            Отчет по страницам
        """
        if not date_from:
            date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        if not date_to:
            date_to = datetime.now().strftime('%Y-%m-%d')
        
        url = f"{REPORTING_API_URL}/data"
        
        params = {
            'ids': counter_id,
            'date1': date_from,
            'date2': date_to,
            'metrics': 'ym:pv:pageviews,ym:pv:users',
            'dimensions': 'ym:pv:URLPath,ym:pv:title',
            'limit': limit
        }
        
        result = self._make_request(url, params=params)
        
        logger.info(f"Отчет по страницам получен для счетчика {counter_id}")
        return result
    
    def get_geo_report(self, counter_id: int,
                      date_from: Optional[str] = None,
                      date_to: Optional[str] = None,
                      limit: int = 100) -> Dict:
        """
        Получение отчета по географии
        
        Args:
            counter_id: ID счетчика
            date_from: Дата начала
            date_to: Дата окончания
            limit: Лимит строк
            
        Returns:
            Отчет по географии
        """
        if not date_from:
            date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        if not date_to:
            date_to = datetime.now().strftime('%Y-%m-%d')
        
        url = f"{REPORTING_API_URL}/data"
        
        params = {
            'ids': counter_id,
            'date1': date_from,
            'date2': date_to,
            'metrics': 'ym:s:visits,ym:s:pageviews,ym:s:users',
            'dimensions': 'ym:s:regionCountry,ym:s:regionCity',
            'limit': limit
        }
        
        result = self._make_request(url, params=params)
        
        logger.info(f"Отчет по географии получен для счетчика {counter_id}")
        return result

