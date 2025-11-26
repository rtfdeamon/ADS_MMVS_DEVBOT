#!/usr/bin/env python3
"""
Детальный анализ посещаемости сайта
"""
import sys
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from data_collector import MetrikaDataCollector
from connector import YandexMetrikaConnector
from oauth import YandexMetrikaOAuth


def load_latest_data():
    """Загрузка последних собранных данных"""
    data_dir = Path(__file__).parent / 'data'
    json_files = sorted(data_dir.glob('yandex_metrika_data_*.json'), reverse=True)
    
    if not json_files:
        print("Данные не найдены. Собираю новые данные...")
        return None
    
    latest_file = json_files[0]
    print(f"Загружаю данные из: {latest_file.name}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_traffic(data):
    """Детальный анализ трафика"""
    print("\n" + "="*70)
    print(" АНАЛИЗ ТРАФИКА")
    print("="*70)
    
    visits_report = data.get('visits_report', {})
    visits_data = visits_report.get('data', [])
    
    if not visits_data:
        print("⚠ Данные о визитах отсутствуют")
        return
    
    # Собираем статистику по дням
    daily_stats = []
    total_visits = 0
    total_pageviews = 0
    total_users = 0
    total_bounce = 0
    total_depth = 0
    total_duration = 0
    
    for row in visits_data:
        dimensions = row.get('dimensions', [])
        metrics = row.get('metrics', [])
        
        if dimensions and len(metrics) >= 6:
            date = dimensions[0].get('name', 'Unknown')
            visits = float(metrics[0]) if metrics[0] else 0
            pageviews = float(metrics[1]) if metrics[1] else 0
            users = float(metrics[2]) if metrics[2] else 0
            bounce_rate = float(metrics[3]) if metrics[3] else 0
            page_depth = float(metrics[4]) if metrics[4] else 0
            duration = float(metrics[5]) if metrics[5] else 0
            
            daily_stats.append({
                'date': date,
                'visits': visits,
                'pageviews': pageviews,
                'users': users,
                'bounce_rate': bounce_rate,
                'page_depth': page_depth,
                'duration': duration
            })
            
            total_visits += visits
            total_pageviews += pageviews
            total_users += users
            total_bounce += bounce_rate
            total_depth += page_depth
            total_duration += duration
    
    days_count = len(daily_stats)
    
    print(f"\n📊 ОБЩАЯ СТАТИСТИКА (за {days_count} дней):")
    print(f"  • Визитов: {total_visits:.0f}")
    print(f"  • Просмотров страниц: {total_pageviews:.0f}")
    print(f"  • Уникальных посетителей: {total_users:.0f}")
    print(f"  • Средний показатель отказов: {(total_bounce/days_count):.1f}%")
    print(f"  • Средняя глубина просмотра: {(total_depth/days_count):.2f} страниц")
    print(f"  • Средняя длительность визита: {(total_duration/days_count):.0f} сек ({(total_duration/days_count/60):.1f} мин)")
    
    # Анализ динамики
    if len(daily_stats) > 1:
        print(f"\n📈 ДИНАМИКА:")
        first_day = daily_stats[0]
        last_day = daily_stats[-1]
        
        visits_change = ((last_day['visits'] - first_day['visits']) / first_day['visits'] * 100) if first_day['visits'] > 0 else 0
        users_change = ((last_day['users'] - first_day['users']) / first_day['users'] * 100) if first_day['users'] > 0 else 0
        
        print(f"  • Визиты: {first_day['visits']:.0f} → {last_day['visits']:.0f} ({visits_change:+.1f}%)")
        print(f"  • Пользователи: {first_day['users']:.0f} → {last_day['users']:.0f} ({users_change:+.1f}%)")
        
        # Лучший и худший день
        best_day = max(daily_stats, key=lambda x: x['visits'])
        worst_day = min(daily_stats, key=lambda x: x['visits'])
        print(f"\n  • Лучший день: {best_day['date']} ({best_day['visits']:.0f} визитов)")
        print(f"  • Худший день: {worst_day['date']} ({worst_day['visits']:.0f} визитов)")
    
    return daily_stats


def analyze_sources(data):
    """Анализ источников трафика"""
    print("\n" + "="*70)
    print(" АНАЛИЗ ИСТОЧНИКОВ ТРАФИКА")
    print("="*70)
    
    sources_report = data.get('sources_report', {})
    sources_data = sources_report.get('data', [])
    
    if not sources_data:
        print("⚠ Данные об источниках отсутствуют")
        return
    
    sources_dict = defaultdict(lambda: {'visits': 0, 'pageviews': 0, 'users': 0})
    engines_dict = defaultdict(lambda: {'visits': 0, 'pageviews': 0, 'users': 0})
    
    for row in sources_data:
        dimensions = row.get('dimensions', [])
        metrics = row.get('metrics', [])
        
        if dimensions and len(metrics) >= 3:
            source = dimensions[0].get('name', 'Unknown')
            engine = dimensions[1].get('name', 'Unknown') if len(dimensions) > 1 else 'Unknown'
            
            visits = float(metrics[0]) if metrics[0] else 0
            pageviews = float(metrics[1]) if metrics[1] else 0
            users = float(metrics[2]) if metrics[2] else 0
            
            sources_dict[source]['visits'] += visits
            sources_dict[source]['pageviews'] += pageviews
            sources_dict[source]['users'] += users
            
            if engine != 'Unknown':
                engines_dict[engine]['visits'] += visits
                engines_dict[engine]['pageviews'] += pageviews
                engines_dict[engine]['users'] += users
    
    total_visits = sum(s['visits'] for s in sources_dict.values())
    
    print(f"\n📊 ТОП ИСТОЧНИКОВ ТРАФИКА:")
    sorted_sources = sorted(sources_dict.items(), key=lambda x: x[1]['visits'], reverse=True)
    
    for i, (source, stats) in enumerate(sorted_sources[:10], 1):
        share = (stats['visits'] / total_visits * 100) if total_visits > 0 else 0
        print(f"  {i:2}. {source:30} | Визитов: {stats['visits']:6.0f} ({share:5.1f}%) | Просмотров: {stats['pageviews']:6.0f}")
    
    if engines_dict:
        print(f"\n🔍 ПОИСКОВЫЕ СИСТЕМЫ:")
        sorted_engines = sorted(engines_dict.items(), key=lambda x: x[1]['visits'], reverse=True)
        for engine, stats in sorted_engines[:5]:
            if engine and engine != 'Unknown':
                share = (stats['visits'] / total_visits * 100) if total_visits > 0 else 0
                engine_name = str(engine) if engine else 'Unknown'
                print(f"  • {engine_name:20} | Визитов: {stats['visits']:6.0f} ({share:5.1f}%)")


def analyze_pages(data):
    """Анализ популярных страниц"""
    print("\n" + "="*70)
    print(" АНАЛИЗ ПОПУЛЯРНЫХ СТРАНИЦ")
    print("="*70)
    
    pages_report = data.get('pages_report', {})
    pages_data = pages_report.get('data', [])
    
    if not pages_data:
        print("⚠ Данные о страницах отсутствуют")
        return
    
    pages_list = []
    for row in pages_data:
        dimensions = row.get('dimensions', [])
        metrics = row.get('metrics', [])
        
        if dimensions and len(metrics) >= 2:
            url = dimensions[0].get('name', 'Unknown')
            title = dimensions[1].get('name', 'Unknown') if len(dimensions) > 1 else 'Unknown'
            
            pageviews = float(metrics[0]) if metrics[0] else 0
            users = float(metrics[1]) if metrics[1] else 0
            
            pages_list.append({
                'url': url,
                'title': title,
                'pageviews': pageviews,
                'users': users
            })
    
    sorted_pages = sorted(pages_list, key=lambda x: x['pageviews'], reverse=True)
    total_pageviews = sum(p['pageviews'] for p in pages_list)
    
    print(f"\n📄 ТОП-20 СТРАНИЦ:")
    for i, page in enumerate(sorted_pages[:20], 1):
        share = (page['pageviews'] / total_pageviews * 100) if total_pageviews > 0 else 0
        url_short = page['url'][:50] + '...' if len(page['url']) > 50 else page['url']
        print(f"  {i:2}. {url_short:52} | Просмотров: {page['pageviews']:6.0f} ({share:5.1f}%) | Пользователей: {page['users']:5.0f}")


def analyze_geo(data):
    """Анализ географии"""
    print("\n" + "="*70)
    print(" АНАЛИЗ ГЕОГРАФИИ ПОСЕТИТЕЛЕЙ")
    print("="*70)
    
    geo_report = data.get('geo_report', {})
    geo_data = geo_report.get('data', [])
    
    if not geo_data:
        print("⚠ Данные о географии отсутствуют")
        return
    
    countries_dict = defaultdict(lambda: {'visits': 0, 'pageviews': 0, 'users': 0})
    cities_list = []
    
    for row in geo_data:
        dimensions = row.get('dimensions', [])
        metrics = row.get('metrics', [])
        
        if dimensions and len(metrics) >= 3:
            country = dimensions[0].get('name', 'Unknown')
            city = dimensions[1].get('name', 'Unknown') if len(dimensions) > 1 else 'Unknown'
            
            visits = float(metrics[0]) if metrics[0] else 0
            pageviews = float(metrics[1]) if metrics[1] else 0
            users = float(metrics[2]) if metrics[2] else 0
            
            countries_dict[country]['visits'] += visits
            countries_dict[country]['pageviews'] += pageviews
            countries_dict[country]['users'] += users
            
            cities_list.append({
                'country': country,
                'city': city,
                'visits': visits,
                'pageviews': pageviews,
                'users': users
            })
    
    total_visits = sum(c['visits'] for c in countries_dict.values())
    
    print(f"\n🌍 ТОП СТРАН:")
    sorted_countries = sorted(countries_dict.items(), key=lambda x: x[1]['visits'], reverse=True)
    for i, (country, stats) in enumerate(sorted_countries[:10], 1):
        share = (stats['visits'] / total_visits * 100) if total_visits > 0 else 0
        print(f"  {i:2}. {country:30} | Визитов: {stats['visits']:6.0f} ({share:5.1f}%) | Пользователей: {stats['users']:5.0f}")
    
    print(f"\n🏙️  ТОП ГОРОДОВ:")
    sorted_cities = sorted(cities_list, key=lambda x: x['visits'], reverse=True)
    for i, city_data in enumerate(sorted_cities[:15], 1):
        share = (city_data['visits'] / total_visits * 100) if total_visits > 0 else 0
        city = str(city_data['city']) if city_data['city'] else 'Unknown'
        country = str(city_data['country']) if city_data['country'] else 'Unknown'
        print(f"  {i:2}. {city:30} ({country:15}) | Визитов: {city_data['visits']:6.0f} ({share:5.1f}%)")


def generate_conclusions(data, daily_stats):
    """Генерация выводов и рекомендаций"""
    print("\n" + "="*70)
    print(" ВЫВОДЫ И РЕКОМЕНДАЦИИ")
    print("="*70)
    
    counter_info = data.get('counter_info', {})
    site_name = counter_info.get('name', 'Сайт')
    site_url = counter_info.get('site', 'N/A')
    
    print(f"\n📋 АНАЛИЗ ДЛЯ: {site_name} ({site_url})")
    
    conclusions = []
    recommendations = []
    
    # Анализ трафика
    if daily_stats:
        avg_visits = sum(d['visits'] for d in daily_stats) / len(daily_stats)
        avg_bounce = sum(d['bounce_rate'] for d in daily_stats) / len(daily_stats)
        avg_depth = sum(d['page_depth'] for d in daily_stats) / len(daily_stats)
        avg_duration = sum(d['duration'] for d in daily_stats) / len(daily_stats)
        
        conclusions.append(f"Средняя посещаемость: {avg_visits:.0f} визитов в день")
        
        if avg_bounce > 70:
            conclusions.append(f"⚠️  Высокий показатель отказов: {avg_bounce:.1f}%")
            recommendations.append("Улучшить релевантность контента и оптимизировать посадочные страницы")
        elif avg_bounce < 40:
            conclusions.append(f"✓ Низкий показатель отказов: {avg_bounce:.1f}% (отлично!)")
        
        if avg_depth < 2:
            conclusions.append(f"⚠️  Низкая глубина просмотра: {avg_depth:.2f} страниц")
            recommendations.append("Добавить внутренние ссылки, улучшить навигацию, создать связанный контент")
        elif avg_depth > 3:
            conclusions.append(f"✓ Хорошая глубина просмотра: {avg_depth:.2f} страниц")
        
        if avg_duration < 60:
            conclusions.append(f"⚠️  Короткое время на сайте: {avg_duration:.0f} сек")
            recommendations.append("Улучшить контент, добавить интерактивные элементы, оптимизировать скорость загрузки")
        elif avg_duration > 180:
            conclusions.append(f"✓ Хорошее время на сайте: {avg_duration:.0f} сек")
    
    # Анализ источников
    sources_report = data.get('sources_report', {})
    sources_data = sources_report.get('data', [])
    if sources_data:
        search_visits = 0
        direct_visits = 0
        total_visits = 0
        
        for row in sources_data:
            dimensions = row.get('dimensions', [])
            metrics = row.get('metrics', [])
            if dimensions and metrics:
                source = dimensions[0].get('name', '').lower()
                visits = float(metrics[0]) if metrics[0] else 0
                total_visits += visits
                
                if 'search' in source or 'поиск' in source:
                    search_visits += visits
                elif 'direct' in source or 'прямой' in source or 'none' in source:
                    direct_visits += visits
        
        if total_visits > 0:
            search_share = (search_visits / total_visits) * 100
            direct_share = (direct_visits / total_visits) * 100
            
            conclusions.append(f"Поисковый трафик: {search_share:.1f}%")
            conclusions.append(f"Прямой трафик: {direct_share:.1f}%")
            
            if search_share < 30:
                recommendations.append("Усилить SEO-оптимизацию и работу с поисковыми системами")
            if direct_share > 50:
                conclusions.append("✓ Высокая доля прямого трафика - хорошая узнаваемость бренда")
    
    print("\n📊 ВЫВОДЫ:")
    for i, conclusion in enumerate(conclusions, 1):
        print(f"  {i}. {conclusion}")
    
    if recommendations:
        print("\n💡 РЕКОМЕНДАЦИИ:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    else:
        print("\n✓ Показатели в норме. Продолжайте текущую стратегию.")


def main():
    """Основная функция"""
    print("\n" + "="*70)
    print(" ДЕТАЛЬНЫЙ АНАЛИЗ ПОСЕЩАЕМОСТИ")
    print("="*70)
    
    # Загружаем данные
    data = load_latest_data()
    
    if not data:
        # Собираем новые данные
        print("\nСобираю новые данные...")
        oauth = YandexMetrikaOAuth()
        token = oauth.get_valid_token()
        
        if not token:
            print("✗ Токен не найден. Запустите авторизацию.")
            return
        
        connector = YandexMetrikaConnector(token=token)
        collector = MetrikaDataCollector(connector)
        
        counters = connector.get_counters()
        if not counters:
            print("✗ Счетчики не найдены")
            return
        
        counter_id = counters[0]['id']
        data = collector.collect_all_data(counter_id=counter_id)
        collector.save_data(data)
    
    # Анализируем
    daily_stats = analyze_traffic(data)
    analyze_sources(data)
    analyze_pages(data)
    analyze_geo(data)
    generate_conclusions(data, daily_stats)
    
    print("\n" + "="*70)
    print(" АНАЛИЗ ЗАВЕРШЕН")
    print("="*70)


if __name__ == '__main__':
    main()

