"""
Основной коннектор для работы с API Яндекс.Директ
"""
import json
import logging
import time
from typing import Dict, List, Optional, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import (
    API_URL,
    YANDEX_DIRECT_TOKEN,
    DEFAULT_CLIENT_LOGIN,
    DEFAULT_LANGUAGE,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    LOG_FORMAT,
    LOG_FILE
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


class YandexDirectConnector:
    """Класс для работы с API Яндекс.Директ"""
    
    def __init__(self, token: Optional[str] = None, client_login: Optional[str] = None):
        """
        Инициализация коннектора
        
        Args:
            token: Токен доступа к API. Если не указан, берется из config.py
            client_login: Логин клиента (для агентских аккаунтов)
        """
        self.token = token or YANDEX_DIRECT_TOKEN
        self.client_login = client_login or DEFAULT_CLIENT_LOGIN
        self.language = DEFAULT_LANGUAGE
        
        if not self.token:
            raise ValueError("Токен Яндекс.Директ не найден! Укажите его в config.txt или переменной окружения YANDEX_DIRECT_TOKEN")
        
        # Настройка сессии с retry
        self.session = requests.Session()
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        
        logger.info("Коннектор Яндекс.Директ инициализирован")
    
    def _make_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Выполнение запроса к API
        
        Args:
            method: Название метода API
            params: Параметры запроса
            
        Returns:
            Ответ от API
        """
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Client-Login': self.client_login,
            'Accept-Language': self.language,
            'Content-Type': 'application/json'
        }
        
        # Удаляем пустые заголовки
        headers = {k: v for k, v in headers.items() if v}
        
        body = {
            'method': method,
            'params': params
        }
        
        try:
            logger.debug(f"Запрос к API: {method}")
            response = self.session.post(
                API_URL,
                headers=headers,
                json=body,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Проверка на ошибки API
            if 'error' in result:
                error = result['error']
                logger.error(f"Ошибка API: {error}")
                raise Exception(f"API Error: {error.get('error_string', 'Unknown error')}")
            
            return result.get('result', {})
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса: {e}")
            raise
    
    def get_campaigns(self, campaign_ids: Optional[List[int]] = None, 
                     field_names: Optional[List[str]] = None) -> List[Dict]:
        """
        Получение списка кампаний
        
        Args:
            campaign_ids: Список ID кампаний (если None - все кампании)
            field_names: Список полей для получения
            
        Returns:
            Список кампаний
        """
        default_fields = [
            'Id', 'Name', 'Type', 'Status', 'State', 'StatusPayment',
            'StartDate', 'EndDate', 'Currency', 'Funds', 'Statistics',
            'DailyBudget', 'TextCampaign', 'SearchStrategy'
        ]
        
        params = {
            'SelectionCriteria': {},
            'FieldNames': field_names or default_fields
        }
        
        if campaign_ids:
            params['SelectionCriteria']['Ids'] = campaign_ids
        
        if self.client_login:
            params['SelectionCriteria']['ClientLogins'] = [self.client_login]
        
        result = self._make_request('campaigns.get', params)
        campaigns = result.get('Campaigns', [])
        
        logger.info(f"Получено кампаний: {len(campaigns)}")
        return campaigns
    
    def get_ad_groups(self, campaign_ids: Optional[List[int]] = None,
                     ad_group_ids: Optional[List[int]] = None,
                     field_names: Optional[List[str]] = None) -> List[Dict]:
        """
        Получение списка групп объявлений
        
        Args:
            campaign_ids: Список ID кампаний
            ad_group_ids: Список ID групп объявлений
            field_names: Список полей для получения
            
        Returns:
            Список групп объявлений
        """
        default_fields = [
            'Id', 'Name', 'CampaignId', 'NegativeKeywords', 'NegativeKeywordSharedSetIds',
            'Type', 'Subtype', 'Status', 'ServingStatus', 'Statistics'
        ]
        
        params = {
            'SelectionCriteria': {},
            'FieldNames': field_names or default_fields
        }
        
        if campaign_ids:
            params['SelectionCriteria']['CampaignIds'] = campaign_ids
        
        if ad_group_ids:
            params['SelectionCriteria']['Ids'] = ad_group_ids
        
        result = self._make_request('adgroups.get', params)
        ad_groups = result.get('AdGroups', [])
        
        logger.info(f"Получено групп объявлений: {len(ad_groups)}")
        return ad_groups
    
    def get_ads(self, campaign_ids: Optional[List[int]] = None,
                ad_group_ids: Optional[List[int]] = None,
                ad_ids: Optional[List[int]] = None,
                field_names: Optional[List[str]] = None) -> List[Dict]:
        """
        Получение списка объявлений
        
        Args:
            campaign_ids: Список ID кампаний
            ad_group_ids: Список ID групп объявлений
            ad_ids: Список ID объявлений
            field_names: Список полей для получения
            
        Returns:
            Список объявлений
        """
        default_fields = [
            'Id', 'AdGroupId', 'CampaignId', 'Type', 'Subtype', 'Status',
            'State', 'StatusModeration', 'TextAd', 'TextImageAd', 'MobileAppAd',
            'DynamicTextAd', 'TextAdBuilderAd', 'Cpc', 'Cpm', 'ImpressionPriority',
            'AdCategories', 'AdExtensionIds', 'VCardId', 'SitelinkSetId',
            'Statistics', 'UserParam1', 'UserParam2'
        ]
        
        params = {
            'SelectionCriteria': {},
            'FieldNames': field_names or default_fields
        }
        
        if campaign_ids:
            params['SelectionCriteria']['CampaignIds'] = campaign_ids
        
        if ad_group_ids:
            params['SelectionCriteria']['AdGroupIds'] = ad_group_ids
        
        if ad_ids:
            params['SelectionCriteria']['Ids'] = ad_ids
        
        result = self._make_request('ads.get', params)
        ads = result.get('Ads', [])
        
        logger.info(f"Получено объявлений: {len(ads)}")
        return ads
    
    def get_keywords(self, campaign_ids: Optional[List[int]] = None,
                    ad_group_ids: Optional[List[int]] = None,
                    keyword_ids: Optional[List[int]] = None,
                    field_names: Optional[List[str]] = None) -> List[Dict]:
        """
        Получение списка ключевых слов
        
        Args:
            campaign_ids: Список ID кампаний
            ad_group_ids: Список ID групп объявлений
            keyword_ids: Список ID ключевых слов
            field_names: Список полей для получения
            
        Returns:
            Список ключевых слов
        """
        default_fields = [
            'Id', 'AdGroupId', 'CampaignId', 'Keyword', 'UserParam1', 'UserParam2',
            'Bid', 'ContextBid', 'StrategyPriority', 'Status', 'State',
            'Productivity', 'StatisticsSearch', 'StatisticsNetwork'
        ]
        
        params = {
            'SelectionCriteria': {},
            'FieldNames': field_names or default_fields
        }
        
        if campaign_ids:
            params['SelectionCriteria']['CampaignIds'] = campaign_ids
        
        if ad_group_ids:
            params['SelectionCriteria']['AdGroupIds'] = ad_group_ids
        
        if keyword_ids:
            params['SelectionCriteria']['Ids'] = keyword_ids
        
        result = self._make_request('keywords.get', params)
        keywords = result.get('Keywords', [])
        
        logger.info(f"Получено ключевых слов: {len(keywords)}")
        return keywords
    
    def get_statistics(self, report_type: str = 'CAMPAIGN_PERFORMANCE_REPORT',
                      date_from: Optional[str] = None,
                      date_to: Optional[str] = None,
                      campaign_ids: Optional[List[int]] = None) -> Dict:
        """
        Получение статистики (требует использования Reports API)
        
        Args:
            report_type: Тип отчета
            date_from: Дата начала (формат YYYY-MM-DD)
            date_to: Дата окончания (формат YYYY-MM-DD)
            campaign_ids: Список ID кампаний
            
        Returns:
            Статистика
        """
        # Это упрощенная версия, для полной реализации нужен Reports API
        logger.warning("Получение статистики требует Reports API. Используйте get_campaigns с полем Statistics")
        return {}
    
    def get_client_info(self) -> Dict:
        """
        Получение информации о клиенте
        
        Returns:
            Информация о клиенте
        """
        params = {
            'FieldNames': ['Login', 'FirstName', 'LastName', 'Currency', 'AgencyName']
        }
        
        result = self._make_request('clients.get', params)
        clients = result.get('Clients', [])
        
        if clients:
            logger.info(f"Информация о клиенте получена: {clients[0].get('Login', 'Unknown')}")
            return clients[0]
        
        return {}

