"""
Модуль для сбора данных из Яндекс.Метрика
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

from connector import YandexMetrikaConnector
from config import DATA_DIR, REPORTS_DIR

logger = logging.getLogger(__name__)


class MetrikaDataCollector:
    """Класс для сбора данных из Яндекс.Метрика"""
    
    def __init__(self, connector: YandexMetrikaConnector):
        """
        Инициализация сборщика данных
        
        Args:
            connector: Экземпляр YandexMetrikaConnector
        """
        self.connector = connector
        self.data_dir = DATA_DIR
        self.reports_dir = REPORTS_DIR
        
        logger.info("MetrikaDataCollector инициализирован")
    
    def collect_all_data(self, counter_id: Optional[int] = None,
                        date_from: Optional[str] = None,
                        date_to: Optional[str] = None) -> Dict:
        """
        Сбор всех данных о счетчике
        
        Args:
            counter_id: ID счетчика (если None - первый доступный)
            date_from: Дата начала (если None - последние 7 дней)
            date_to: Дата окончания (если None - сегодня)
            
        Returns:
            Словарь со всеми собранными данными
        """
        logger.info("Начало сбора данных...")
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'counters': [],
            'counter_info': {},
            'goals': [],
            'filters': [],
            'visits_report': {},
            'sources_report': {},
            'pages_report': {},
            'geo_report': {}
        }
        
        try:
            # Получаем список счетчиков
            counters = self.connector.get_counters()
            data['counters'] = counters
            
            if not counters:
                logger.warning("Счетчики не найдены")
                return data
            
            # Используем указанный счетчик или первый доступный
            if not counter_id:
                counter_id = counters[0]['id']
            
            logger.info(f"Используется счетчик: {counter_id}")
            
            # Информация о счетчике
            data['counter_info'] = self.connector.get_counter_info(counter_id)
            
            # Цели
            data['goals'] = self.connector.get_goals(counter_id)
            
            # Фильтры
            data['filters'] = self.connector.get_filters(counter_id)
            
            # Устанавливаем даты по умолчанию
            if not date_from:
                date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            if not date_to:
                date_to = datetime.now().strftime('%Y-%m-%d')
            
            # Отчеты
            data['visits_report'] = self.connector.get_visits_report(
                counter_id, date_from, date_to
            )
            
            data['sources_report'] = self.connector.get_sources_report(
                counter_id, date_from, date_to
            )
            
            data['pages_report'] = self.connector.get_pages_report(
                counter_id, date_from, date_to
            )
            
            data['geo_report'] = self.connector.get_geo_report(
                counter_id, date_from, date_to
            )
            
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
            filename: Имя файла
            
        Returns:
            Путь к сохраненному файлу
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'yandex_metrika_data_{timestamp}.json'
        
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
            filename = f'yandex_metrika_report_{timestamp}.xlsx'
        
        filepath = self.reports_dir / filename
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Счетчики
            if data.get('counters'):
                df_counters = pd.DataFrame(data['counters'])
                df_counters.to_excel(writer, sheet_name='Счетчики', index=False)
            
            # Информация о счетчике
            if data.get('counter_info'):
                df_info = pd.DataFrame([data['counter_info']])
                df_info.to_excel(writer, sheet_name='Информация о счетчике', index=False)
            
            # Цели
            if data.get('goals'):
                df_goals = pd.DataFrame(data['goals'])
                df_goals.to_excel(writer, sheet_name='Цели', index=False)
            
            # Отчет о визитах
            if data.get('visits_report', {}).get('data'):
                visits_data = data['visits_report']['data']
                if visits_data:
                    df_visits = pd.DataFrame(visits_data)
                    df_visits.to_excel(writer, sheet_name='Визиты', index=False)
            
            # Отчет по источникам
            if data.get('sources_report', {}).get('data'):
                sources_data = data['sources_report']['data']
                if sources_data:
                    df_sources = pd.DataFrame(sources_data)
                    df_sources.to_excel(writer, sheet_name='Источники', index=False)
            
            # Отчет по страницам
            if data.get('pages_report', {}).get('data'):
                pages_data = data['pages_report']['data']
                if pages_data:
                    df_pages = pd.DataFrame(pages_data)
                    df_pages.to_excel(writer, sheet_name='Страницы', index=False)
            
            # Отчет по географии
            if data.get('geo_report', {}).get('data'):
                geo_data = data['geo_report']['data']
                if geo_data:
                    df_geo = pd.DataFrame(geo_data)
                    df_geo.to_excel(writer, sheet_name='География', index=False)
            
            # Сводная информация
            summary = {
                'Метрика': [
                    'Всего счетчиков',
                    'Целей',
                    'Фильтров',
                    'Дата сбора данных'
                ],
                'Значение': [
                    len(data.get('counters', [])),
                    len(data.get('goals', [])),
                    len(data.get('filters', [])),
                    data.get('timestamp', 'N/A')
                ]
            }
            df_summary = pd.DataFrame(summary)
            df_summary.to_excel(writer, sheet_name='Сводка', index=False)
        
        logger.info(f"Данные экспортированы в Excel: {filepath}")
        return filepath

