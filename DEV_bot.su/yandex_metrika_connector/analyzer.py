"""
Модуль для анализа данных Яндекс.Метрика
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

from config import REPORTS_DIR

logger = logging.getLogger(__name__)


class MetrikaAnalyzer:
    """Класс для анализа данных Яндекс.Метрика"""
    
    def __init__(self):
        """Инициализация анализатора"""
        self.reports_dir = REPORTS_DIR
        logger.info("MetrikaAnalyzer инициализирован")
    
    def analyze_data(self, data: Dict) -> Dict:
        """
        Анализ данных Метрики
        
        Args:
            data: Данные о счетчике и отчеты
            
        Returns:
            Результаты анализа
        """
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'summary': {},
            'traffic_analysis': {},
            'sources_analysis': {},
            'pages_analysis': {},
            'geo_analysis': {},
            'recommendations': []
        }
        
        # Общая статистика
        counters = data.get('counters', [])
        counter_info = data.get('counter_info', {})
        goals = data.get('goals', [])
        
        analysis['summary'] = {
            'total_counters': len(counters),
            'counter_name': counter_info.get('name', 'N/A'),
            'counter_site': counter_info.get('site', 'N/A'),
            'total_goals': len(goals),
            'counter_status': counter_info.get('status', 'N/A')
        }
        
        # Анализ трафика
        visits_report = data.get('visits_report', {})
        if visits_report.get('data'):
            analysis['traffic_analysis'] = self._analyze_traffic(visits_report)
        
        # Анализ источников
        sources_report = data.get('sources_report', {})
        if sources_report.get('data'):
            analysis['sources_analysis'] = self._analyze_sources(sources_report)
        
        # Анализ страниц
        pages_report = data.get('pages_report', {})
        if pages_report.get('data'):
            analysis['pages_analysis'] = self._analyze_pages(pages_report)
        
        # Анализ географии
        geo_report = data.get('geo_report', {})
        if geo_report.get('data'):
            analysis['geo_analysis'] = self._analyze_geo(geo_report)
        
        # Рекомендации
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _analyze_traffic(self, visits_report: Dict) -> Dict:
        """Анализ трафика"""
        data_rows = visits_report.get('data', [])
        
        if not data_rows:
            return {}
        
        analysis = {
            'total_visits': 0,
            'total_pageviews': 0,
            'total_users': 0,
            'avg_bounce_rate': 0,
            'avg_page_depth': 0,
            'avg_visit_duration': 0,
            'daily_stats': []
        }
        
        total_visits = 0
        total_pageviews = 0
        total_users = 0
        total_bounce_rate = 0
        total_page_depth = 0
        total_duration = 0
        count = 0
        
        for row in data_rows:
            metrics = row.get('metrics', [])
            if len(metrics) >= 6:
                visits = float(metrics[0]) if metrics[0] else 0
                pageviews = float(metrics[1]) if metrics[1] else 0
                users = float(metrics[2]) if metrics[2] else 0
                bounce_rate = float(metrics[3]) if metrics[3] else 0
                page_depth = float(metrics[4]) if metrics[4] else 0
                duration = float(metrics[5]) if metrics[5] else 0
                
                total_visits += visits
                total_pageviews += pageviews
                total_users += users
                total_bounce_rate += bounce_rate
                total_page_depth += page_depth
                total_duration += duration
                count += 1
                
                dimensions = row.get('dimensions', [])
                date = dimensions[0].get('name', 'N/A') if dimensions else 'N/A'
                
                analysis['daily_stats'].append({
                    'date': date,
                    'visits': visits,
                    'pageviews': pageviews,
                    'users': users,
                    'bounce_rate': bounce_rate,
                    'page_depth': page_depth,
                    'duration': duration
                })
        
        if count > 0:
            analysis['total_visits'] = total_visits
            analysis['total_pageviews'] = total_pageviews
            analysis['total_users'] = total_users
            analysis['avg_bounce_rate'] = total_bounce_rate / count
            analysis['avg_page_depth'] = total_page_depth / count
            analysis['avg_visit_duration'] = total_duration / count
        
        return analysis
    
    def _analyze_sources(self, sources_report: Dict) -> Dict:
        """Анализ источников трафика"""
        data_rows = sources_report.get('data', [])
        
        if not data_rows:
            return {}
        
        analysis = {
            'top_sources': [],
            'by_engine': {}
        }
        
        sources_dict = {}
        
        for row in data_rows:
            dimensions = row.get('dimensions', [])
            metrics = row.get('metrics', [])
            
            if dimensions and metrics:
                source = dimensions[0].get('name', 'Unknown')
                engine = dimensions[1].get('name', 'Unknown') if len(dimensions) > 1 else 'Unknown'
                
                visits = float(metrics[0]) if metrics[0] else 0
                pageviews = float(metrics[1]) if metrics[1] else 0
                users = float(metrics[2]) if metrics[2] else 0
                
                if source not in sources_dict:
                    sources_dict[source] = {
                        'source': source,
                        'visits': 0,
                        'pageviews': 0,
                        'users': 0
                    }
                
                sources_dict[source]['visits'] += visits
                sources_dict[source]['pageviews'] += pageviews
                sources_dict[source]['users'] += users
                
                if engine not in analysis['by_engine']:
                    analysis['by_engine'][engine] = {
                        'visits': 0,
                        'pageviews': 0,
                        'users': 0
                    }
                
                analysis['by_engine'][engine]['visits'] += visits
                analysis['by_engine'][engine]['pageviews'] += pageviews
                analysis['by_engine'][engine]['users'] += users
        
        # Топ источников
        analysis['top_sources'] = sorted(
            sources_dict.values(),
            key=lambda x: x['visits'],
            reverse=True
        )[:10]
        
        return analysis
    
    def _analyze_pages(self, pages_report: Dict) -> Dict:
        """Анализ страниц"""
        data_rows = pages_report.get('data', [])
        
        if not data_rows:
            return {}
        
        analysis = {
            'top_pages': []
        }
        
        pages_list = []
        
        for row in data_rows:
            dimensions = row.get('dimensions', [])
            metrics = row.get('metrics', [])
            
            if dimensions and metrics:
                url = dimensions[0].get('name', 'Unknown')
                title = dimensions[1].get('name', 'Unknown') if len(dimensions) > 1 else 'Unknown'
                
                pageviews = float(metrics[0]) if len(metrics) > 0 and metrics[0] else 0
                users = float(metrics[1]) if len(metrics) > 1 and metrics[1] else 0
                
                pages_list.append({
                    'url': url,
                    'title': title,
                    'pageviews': pageviews,
                    'users': users
                })
        
        # Топ страниц
        analysis['top_pages'] = sorted(
            pages_list,
            key=lambda x: x['pageviews'],
            reverse=True
        )[:20]
        
        return analysis
    
    def _analyze_geo(self, geo_report: Dict) -> Dict:
        """Анализ географии"""
        data_rows = geo_report.get('data', [])
        
        if not data_rows:
            return {}
        
        analysis = {
            'by_country': {},
            'by_city': []
        }
        
        cities_list = []
        
        for row in data_rows:
            dimensions = row.get('dimensions', [])
            metrics = row.get('metrics', [])
            
            if dimensions and metrics:
                country = dimensions[0].get('name', 'Unknown')
                city = dimensions[1].get('name', 'Unknown') if len(dimensions) > 1 else 'Unknown'
                
                visits = float(metrics[0]) if metrics[0] else 0
                pageviews = float(metrics[1]) if metrics[1] else 0
                users = float(metrics[2]) if metrics[2] else 0
                
                if country not in analysis['by_country']:
                    analysis['by_country'][country] = {
                        'visits': 0,
                        'pageviews': 0,
                        'users': 0
                    }
                
                analysis['by_country'][country]['visits'] += visits
                analysis['by_country'][country]['pageviews'] += pageviews
                analysis['by_country'][country]['users'] += users
                
                cities_list.append({
                    'country': country,
                    'city': city,
                    'visits': visits,
                    'pageviews': pageviews,
                    'users': users
                })
        
        # Топ городов
        analysis['by_city'] = sorted(
            cities_list,
            key=lambda x: x['visits'],
            reverse=True
        )[:20]
        
        return analysis
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Генерация рекомендаций"""
        recommendations = []
        
        # Анализ трафика
        traffic = analysis.get('traffic_analysis', {})
        if traffic:
            bounce_rate = traffic.get('avg_bounce_rate', 0)
            if bounce_rate > 70:
                recommendations.append(
                    f"Высокий показатель отказов ({bounce_rate:.1f}%). "
                    "Рекомендуется улучшить релевантность контента и оптимизировать посадочные страницы."
                )
            
            page_depth = traffic.get('avg_page_depth', 0)
            if page_depth < 2:
                recommendations.append(
                    f"Низкая глубина просмотра ({page_depth:.1f} страниц). "
                    "Рекомендуется улучшить навигацию и добавить внутренние ссылки."
                )
        
        # Анализ источников
        sources = analysis.get('sources_analysis', {})
        if sources:
            top_sources = sources.get('top_sources', [])
            if top_sources:
                search_visits = sum(s.get('visits', 0) for s in top_sources if 'search' in s.get('source', '').lower())
                total_visits = sum(s.get('visits', 0) for s in top_sources)
                if total_visits > 0:
                    search_share = (search_visits / total_visits) * 100
                    if search_share < 30:
                        recommendations.append(
                            f"Низкая доля поискового трафика ({search_share:.1f}%). "
                            "Рекомендуется усилить SEO и работу с поисковыми системами."
                        )
        
        # Анализ страниц
        pages = analysis.get('pages_analysis', {})
        if pages:
            top_pages = pages.get('top_pages', [])
            if top_pages:
                home_visits = sum(p.get('visits', 0) for p in top_pages if p.get('url', '') == '/')
                if home_visits == 0:
                    recommendations.append(
                        "Главная страница не входит в топ страниц. "
                        "Рекомендуется улучшить главную страницу и увеличить ее привлекательность."
                    )
        
        if not recommendations:
            recommendations.append("Общие показатели в норме. Продолжайте мониторинг и оптимизацию.")
        
        return recommendations
    
    def save_analysis(self, analysis: Dict, filename: Optional[str] = None) -> Path:
        """Сохранение анализа"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'metrika_analysis_{timestamp}.json'
        
        filepath = self.reports_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Анализ сохранен в {filepath}")
        return filepath
    
    def export_analysis_report(self, analysis: Dict, filename: Optional[str] = None) -> Path:
        """Экспорт анализа в Excel"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'metrika_analysis_{timestamp}.xlsx'
        
        filepath = self.reports_dir / filename
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Сводка
            summary = analysis.get('summary', {})
            df_summary = pd.DataFrame([summary])
            df_summary.to_excel(writer, sheet_name='Сводка', index=False)
            
            # Анализ трафика
            traffic = analysis.get('traffic_analysis', {})
            if traffic:
                traffic_summary = {
                    'Метрика': [
                        'Всего визитов',
                        'Всего просмотров',
                        'Всего пользователей',
                        'Средний показатель отказов (%)',
                        'Средняя глубина просмотра',
                        'Средняя длительность визита (сек)'
                    ],
                    'Значение': [
                        traffic.get('total_visits', 0),
                        traffic.get('total_pageviews', 0),
                        traffic.get('total_users', 0),
                        f"{traffic.get('avg_bounce_rate', 0):.2f}",
                        f"{traffic.get('avg_page_depth', 0):.2f}",
                        f"{traffic.get('avg_visit_duration', 0):.2f}"
                    ]
                }
                df_traffic = pd.DataFrame(traffic_summary)
                df_traffic.to_excel(writer, sheet_name='Анализ трафика', index=False)
                
                if traffic.get('daily_stats'):
                    df_daily = pd.DataFrame(traffic['daily_stats'])
                    df_daily.to_excel(writer, sheet_name='Статистика по дням', index=False)
            
            # Топ источников
            sources = analysis.get('sources_analysis', {})
            if sources.get('top_sources'):
                df_sources = pd.DataFrame(sources['top_sources'])
                df_sources.to_excel(writer, sheet_name='Топ источников', index=False)
            
            # Топ страниц
            pages = analysis.get('pages_analysis', {})
            if pages.get('top_pages'):
                df_pages = pd.DataFrame(pages['top_pages'])
                df_pages.to_excel(writer, sheet_name='Топ страниц', index=False)
            
            # Топ городов
            geo = analysis.get('geo_analysis', {})
            if geo.get('by_city'):
                df_cities = pd.DataFrame(geo['by_city'])
                df_cities.to_excel(writer, sheet_name='Топ городов', index=False)
            
            # Рекомендации
            recommendations = analysis.get('recommendations', [])
            if recommendations:
                df_rec = pd.DataFrame({'Рекомендация': recommendations})
                df_rec.to_excel(writer, sheet_name='Рекомендации', index=False)
        
        logger.info(f"Отчет об анализе экспортирован: {filepath}")
        return filepath

