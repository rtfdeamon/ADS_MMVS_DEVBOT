"""
Модуль для сбора данных о кампаниях, объявлениях и стратегии
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

from connector import YandexDirectConnector
from config import DATA_DIR, REPORTS_DIR

logger = logging.getLogger(__name__)


class DataCollector:
    """Класс для сбора данных из Яндекс.Директ"""
    
    def __init__(self, connector: YandexDirectConnector):
        """
        Инициализация сборщика данных
        
        Args:
            connector: Экземпляр YandexDirectConnector
        """
        self.connector = connector
        self.data_dir = DATA_DIR
        self.reports_dir = REPORTS_DIR
        
        logger.info("DataCollector инициализирован")
    
    def collect_all_data(self, campaign_ids: Optional[List[int]] = None) -> Dict:
        """
        Сбор всех данных о кампаниях
        
        Args:
            campaign_ids: Список ID кампаний (если None - все кампании)
            
        Returns:
            Словарь со всеми собранными данными
        """
        logger.info("Начало сбора данных...")
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'client_info': {},
            'campaigns': [],
            'ad_groups': [],
            'ads': [],
            'keywords': []
        }
        
        try:
            # Информация о клиенте
            data['client_info'] = self.connector.get_client_info()
            
            # Кампании
            campaigns = self.connector.get_campaigns(campaign_ids=campaign_ids)
            data['campaigns'] = campaigns
            
            if campaigns:
                campaign_ids_list = [c['Id'] for c in campaigns]
                
                # Группы объявлений
                ad_groups = self.connector.get_ad_groups(campaign_ids=campaign_ids_list)
                data['ad_groups'] = ad_groups
                
                ad_group_ids_list = [ag['Id'] for ag in ad_groups]
                
                # Объявления
                ads = self.connector.get_ads(
                    campaign_ids=campaign_ids_list,
                    ad_group_ids=ad_group_ids_list
                )
                data['ads'] = ads
                
                # Ключевые слова
                keywords = self.connector.get_keywords(
                    campaign_ids=campaign_ids_list,
                    ad_group_ids=ad_group_ids_list
                )
                data['keywords'] = keywords
            
            logger.info("Сбор данных завершен успешно")
            return data
            
        except Exception as e:
            logger.error(f"Ошибка при сборе данных: {e}")
            raise
    
    def save_data(self, data: Dict, filename: Optional[str] = None) -> Path:
        """
        Сохранение данных в JSON файл
        
        Args:
            data: Данные для сохранения
            filename: Имя файла (если None - генерируется автоматически)
            
        Returns:
            Путь к сохраненному файлу
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'yandex_direct_data_{timestamp}.json'
        
        filepath = self.data_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Данные сохранены в {filepath}")
        return filepath
    
    def load_data(self, filename: str) -> Dict:
        """
        Загрузка данных из JSON файла
        
        Args:
            filename: Имя файла
            
        Returns:
            Загруженные данные
        """
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Файл не найден: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Данные загружены из {filepath}")
        return data
    
    def export_to_excel(self, data: Dict, filename: Optional[str] = None) -> Path:
        """
        Экспорт данных в Excel файл
        
        Args:
            data: Данные для экспорта
            filename: Имя файла
            
        Returns:
            Путь к сохраненному файлу
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'yandex_direct_report_{timestamp}.xlsx'
        
        filepath = self.reports_dir / filename
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Кампании
            if data.get('campaigns'):
                df_campaigns = pd.DataFrame(data['campaigns'])
                df_campaigns.to_excel(writer, sheet_name='Кампании', index=False)
            
            # Группы объявлений
            if data.get('ad_groups'):
                df_ad_groups = pd.DataFrame(data['ad_groups'])
                df_ad_groups.to_excel(writer, sheet_name='Группы объявлений', index=False)
            
            # Объявления
            if data.get('ads'):
                df_ads = pd.DataFrame(data['ads'])
                df_ads.to_excel(writer, sheet_name='Объявления', index=False)
            
            # Ключевые слова
            if data.get('keywords'):
                df_keywords = pd.DataFrame(data['keywords'])
                df_keywords.to_excel(writer, sheet_name='Ключевые слова', index=False)
            
            # Сводная информация
            summary = {
                'Метрика': [
                    'Всего кампаний',
                    'Всего групп объявлений',
                    'Всего объявлений',
                    'Всего ключевых слов',
                    'Дата сбора данных'
                ],
                'Значение': [
                    len(data.get('campaigns', [])),
                    len(data.get('ad_groups', [])),
                    len(data.get('ads', [])),
                    len(data.get('keywords', [])),
                    data.get('timestamp', 'N/A')
                ]
            }
            df_summary = pd.DataFrame(summary)
            df_summary.to_excel(writer, sheet_name='Сводка', index=False)
        
        logger.info(f"Данные экспортированы в Excel: {filepath}")
        return filepath
    
    def get_campaign_structure(self, campaign_id: int) -> Dict:
        """
        Получение полной структуры кампании
        
        Args:
            campaign_id: ID кампании
            
        Returns:
            Структура кампании с вложенными элементами
        """
        campaigns = self.connector.get_campaigns(campaign_ids=[campaign_id])
        
        if not campaigns:
            return {}
        
        campaign = campaigns[0]
        
        # Получаем связанные данные
        ad_groups = self.connector.get_ad_groups(campaign_ids=[campaign_id])
        
        ad_group_ids = [ag['Id'] for ag in ad_groups]
        ads = self.connector.get_ads(ad_group_ids=ad_group_ids)
        keywords = self.connector.get_keywords(ad_group_ids=ad_group_ids)
        
        # Формируем структуру
        structure = {
            'campaign': campaign,
            'ad_groups': []
        }
        
        for ad_group in ad_groups:
            ag_id = ad_group['Id']
            group_ads = [ad for ad in ads if ad.get('AdGroupId') == ag_id]
            group_keywords = [kw for kw in keywords if kw.get('AdGroupId') == ag_id]
            
            structure['ad_groups'].append({
                'ad_group': ad_group,
                'ads': group_ads,
                'keywords': group_keywords
            })
        
        return structure

