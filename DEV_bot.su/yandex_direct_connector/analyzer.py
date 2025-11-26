"""
Модуль для анализа стратегии поведения в Яндекс.Директ
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

from config import REPORTS_DIR

logger = logging.getLogger(__name__)


class StrategyAnalyzer:
    """Класс для анализа стратегии рекламных кампаний"""
    
    def __init__(self):
        """Инициализация анализатора"""
        self.reports_dir = REPORTS_DIR
        logger.info("StrategyAnalyzer инициализирован")
    
    def analyze_campaigns(self, data: Dict) -> Dict:
        """
        Анализ кампаний
        
        Args:
            data: Данные о кампаниях
            
        Returns:
            Результаты анализа
        """
        campaigns = data.get('campaigns', [])
        ad_groups = data.get('ad_groups', [])
        ads = data.get('ads', [])
        keywords = data.get('keywords', [])
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'summary': {},
            'campaign_analysis': [],
            'keyword_analysis': {},
            'recommendations': []
        }
        
        # Общая статистика
        analysis['summary'] = {
            'total_campaigns': len(campaigns),
            'total_ad_groups': len(ad_groups),
            'total_ads': len(ads),
            'total_keywords': len(keywords),
            'active_campaigns': len([c for c in campaigns if c.get('Status') == 'ACCEPTED']),
            'paused_campaigns': len([c for c in campaigns if c.get('Status') == 'PAUSED']),
            'archived_campaigns': len([c for c in campaigns if c.get('Status') == 'ARCHIVED'])
        }
        
        # Анализ по кампаниям
        for campaign in campaigns:
            campaign_id = campaign.get('Id')
            campaign_ads = [ad for ad in ads if ad.get('CampaignId') == campaign_id]
            campaign_keywords = [kw for kw in keywords if kw.get('CampaignId') == campaign_id]
            campaign_ad_groups = [ag for ag in ad_groups if ag.get('CampaignId') == campaign_id]
            
            campaign_analysis = {
                'campaign_id': campaign_id,
                'campaign_name': campaign.get('Name', 'N/A'),
                'status': campaign.get('Status', 'N/A'),
                'type': campaign.get('Type', 'N/A'),
                'ad_groups_count': len(campaign_ad_groups),
                'ads_count': len(campaign_ads),
                'keywords_count': len(campaign_keywords),
                'strategy': self._extract_strategy(campaign),
                'budget': self._extract_budget(campaign)
            }
            
            analysis['campaign_analysis'].append(campaign_analysis)
        
        # Анализ ключевых слов
        analysis['keyword_analysis'] = self._analyze_keywords(keywords)
        
        # Рекомендации
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _extract_strategy(self, campaign: Dict) -> Dict:
        """Извлечение информации о стратегии кампании"""
        strategy_info = {
            'type': 'Unknown',
            'details': {}
        }
        
        # Поиск стратегии в разных полях
        if 'TextCampaign' in campaign:
            text_campaign = campaign['TextCampaign']
            if 'BiddingStrategy' in text_campaign:
                bidding = text_campaign['BiddingStrategy']
                strategy_info['type'] = bidding.get('Search', {}).get('BiddingStrategyType', 'Unknown')
                strategy_info['details'] = bidding.get('Search', {})
        
        if 'SearchStrategy' in campaign:
            strategy_info['type'] = campaign['SearchStrategy'].get('BiddingStrategyType', 'Unknown')
            strategy_info['details'] = campaign['SearchStrategy']
        
        return strategy_info
    
    def _extract_budget(self, campaign: Dict) -> Dict:
        """Извлечение информации о бюджете"""
        budget_info = {
            'daily_budget': None,
            'funds': {}
        }
        
        if 'DailyBudget' in campaign:
            budget_info['daily_budget'] = campaign['DailyBudget']
        
        if 'Funds' in campaign:
            budget_info['funds'] = campaign['Funds']
        
        return budget_info
    
    def _analyze_keywords(self, keywords: List[Dict]) -> Dict:
        """Анализ ключевых слов"""
        if not keywords:
            return {}
        
        analysis = {
            'total': len(keywords),
            'by_status': {},
            'by_bid_range': {},
            'top_keywords': []
        }
        
        # Группировка по статусам
        statuses = {}
        for kw in keywords:
            status = kw.get('Status', 'Unknown')
            statuses[status] = statuses.get(status, 0) + 1
        analysis['by_status'] = statuses
        
        # Анализ ставок
        bids = [kw.get('Bid', 0) for kw in keywords if kw.get('Bid')]
        if bids:
            analysis['by_bid_range'] = {
                'min': min(bids),
                'max': max(bids),
                'avg': sum(bids) / len(bids)
            }
        
        # Топ ключевых слов (по ставке)
        sorted_keywords = sorted(
            [kw for kw in keywords if kw.get('Bid')],
            key=lambda x: x.get('Bid', 0),
            reverse=True
        )[:10]
        
        analysis['top_keywords'] = [
            {
                'keyword': kw.get('Keyword', 'N/A'),
                'bid': kw.get('Bid', 0),
                'status': kw.get('Status', 'N/A')
            }
            for kw in sorted_keywords
        ]
        
        return analysis
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Генерация рекомендаций на основе анализа"""
        recommendations = []
        
        summary = analysis.get('summary', {})
        
        # Проверка на приостановленные кампании
        if summary.get('paused_campaigns', 0) > 0:
            recommendations.append(
                f"Обнаружено {summary['paused_campaigns']} приостановленных кампаний. "
                "Рекомендуется проверить причины остановки и возобновить работу активных кампаний."
            )
        
        # Проверка на архивированные кампании
        if summary.get('archived_campaigns', 0) > 0:
            recommendations.append(
                f"Обнаружено {summary['archived_campaigns']} архивированных кампаний. "
                "Рассмотрите возможность удаления или восстановления."
            )
        
        # Анализ ключевых слов
        keyword_analysis = analysis.get('keyword_analysis', {})
        if keyword_analysis.get('total', 0) == 0:
            recommendations.append(
                "Не найдено ключевых слов. Рекомендуется добавить ключевые слова для всех групп объявлений."
            )
        
        # Проверка распределения ставок
        bid_range = keyword_analysis.get('by_bid_range', {})
        if bid_range.get('max', 0) > 0:
            max_bid = bid_range['max']
            avg_bid = bid_range.get('avg', 0)
            if max_bid > avg_bid * 3:
                recommendations.append(
                    f"Обнаружен большой разброс ставок (макс: {max_bid:.2f}, средняя: {avg_bid:.2f}). "
                    "Рекомендуется оптимизировать ставки для более равномерного распределения бюджета."
                )
        
        # Проверка количества объявлений
        total_ads = summary.get('total_ads', 0)
        total_ad_groups = summary.get('total_ad_groups', 0)
        if total_ad_groups > 0:
            avg_ads_per_group = total_ads / total_ad_groups
            if avg_ads_per_group < 2:
                recommendations.append(
                    f"Среднее количество объявлений на группу: {avg_ads_per_group:.1f}. "
                    "Рекомендуется создавать минимум 2-3 варианта объявлений для каждой группы."
                )
        
        if not recommendations:
            recommendations.append("Общая структура кампаний выглядит хорошо. Продолжайте мониторинг эффективности.")
        
        return recommendations
    
    def save_analysis(self, analysis: Dict, filename: Optional[str] = None) -> Path:
        """
        Сохранение анализа в JSON файл
        
        Args:
            analysis: Результаты анализа
            filename: Имя файла
            
        Returns:
            Путь к сохраненному файлу
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'strategy_analysis_{timestamp}.json'
        
        filepath = self.reports_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Анализ сохранен в {filepath}")
        return filepath
    
    def export_analysis_report(self, analysis: Dict, filename: Optional[str] = None) -> Path:
        """
        Экспорт анализа в Excel
        
        Args:
            analysis: Результаты анализа
            filename: Имя файла
            
        Returns:
            Путь к сохраненному файлу
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'strategy_analysis_{timestamp}.xlsx'
        
        filepath = self.reports_dir / filename
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Сводка
            summary = analysis.get('summary', {})
            df_summary = pd.DataFrame([summary])
            df_summary.to_excel(writer, sheet_name='Сводка', index=False)
            
            # Анализ кампаний
            if analysis.get('campaign_analysis'):
                df_campaigns = pd.DataFrame(analysis['campaign_analysis'])
                df_campaigns.to_excel(writer, sheet_name='Анализ кампаний', index=False)
            
            # Анализ ключевых слов
            keyword_analysis = analysis.get('keyword_analysis', {})
            if keyword_analysis:
                # Статусы
                if keyword_analysis.get('by_status'):
                    df_status = pd.DataFrame([
                        {'Статус': k, 'Количество': v}
                        for k, v in keyword_analysis['by_status'].items()
                    ])
                    df_status.to_excel(writer, sheet_name='Статусы ключевых слов', index=False)
                
                # Топ ключевых слов
                if keyword_analysis.get('top_keywords'):
                    df_top = pd.DataFrame(keyword_analysis['top_keywords'])
                    df_top.to_excel(writer, sheet_name='Топ ключевых слов', index=False)
            
            # Рекомендации
            recommendations = analysis.get('recommendations', [])
            if recommendations:
                df_rec = pd.DataFrame({'Рекомендация': recommendations})
                df_rec.to_excel(writer, sheet_name='Рекомендации', index=False)
        
        logger.info(f"Отчет об анализе экспортирован: {filepath}")
        return filepath

