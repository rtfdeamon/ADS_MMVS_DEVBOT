#!/usr/bin/env python3
"""
Скрипт для получения статистики по dev-bot
"""
import sys
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from oauth import YandexMetrikaOAuth
from connector import YandexMetrikaConnector
from data_collector import MetrikaDataCollector
from analyzer import MetrikaAnalyzer
from datetime import datetime, timedelta


def find_devbot_counter(connector):
    """Поиск счетчика для dev-bot"""
    counters = connector.get_counters()
    
    print(f"\nНайдено счетчиков: {len(counters)}")
    print("\nДоступные счетчики:")
    for counter in counters:
        site = counter.get('site', 'N/A')
        name = counter.get('name', 'N/A')
        counter_id = counter.get('id')
        print(f"  - ID: {counter_id}, Имя: {name}, Сайт: {site}")
    
    # Ищем счетчик для dev-bot
    devbot_counter = None
    for counter in counters:
        site = counter.get('site', '').lower()
        name = counter.get('name', '').lower()
        if 'dev-bot' in site or 'dev-bot' in name or 'devbot' in site or 'devbot' in name:
            devbot_counter = counter
            break
    
    # Если не нашли, используем первый счетчик (или можно попросить выбрать)
    if not devbot_counter and counters:
        print("\n⚠ Счетчик для dev-bot не найден. Используется первый доступный счетчик.")
        devbot_counter = counters[0]
    
    return devbot_counter


def main():
    """Основная функция"""
    print("\n" + "="*70)
    print(" ПОЛУЧЕНИЕ СТАТИСТИКИ ДЛЯ DEV-BOT")
    print("="*70)
    
    # Проверяем токен
    print("\n[1/4] Проверка токена доступа...")
    oauth = YandexMetrikaOAuth()
    token_data = oauth.load_token()
    
    if not token_data or not token_data.get('access_token'):
        print("✗ Токен не найден. Запустите oauth.py для авторизации.")
        return
    
    token = token_data.get('access_token')
    print("✓ Токен найден")
    
    # Инициализация коннектора
    print("\n[2/4] Инициализация коннектора...")
    try:
        connector = YandexMetrikaConnector(token=token)
        print("✓ Коннектор инициализирован")
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return
    
    # Поиск счетчика для dev-bot
    print("\n[3/4] Поиск счетчика для dev-bot...")
    devbot_counter = find_devbot_counter(connector)
    
    if not devbot_counter:
        print("✗ Счетчики не найдены")
        return
    
    counter_id = devbot_counter['id']
    counter_name = devbot_counter.get('name', 'N/A')
    counter_site = devbot_counter.get('site', 'N/A')
    
    print(f"✓ Используется счетчик: {counter_name} (ID: {counter_id})")
    print(f"  Сайт: {counter_site}")
    
    # Сбор данных за последние 30 дней
    print("\n[4/4] Сбор данных...")
    try:
        collector = MetrikaDataCollector(connector)
        
        # Устанавливаем период: последние 30 дней
        date_to = datetime.now().strftime('%Y-%m-%d')
        date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        print(f"  Период: {date_from} - {date_to}")
        
        data = collector.collect_all_data(
            counter_id=counter_id,
            date_from=date_from,
            date_to=date_to
        )
        
        print(f"  ✓ Данные собраны:")
        print(f"    - Целей: {len(data.get('goals', []))}")
        print(f"    - Фильтров: {len(data.get('filters', []))}")
        
        visits_data = data.get('visits_report', {}).get('data', [])
        print(f"    - Записей в отчете о визитах: {len(visits_data)}")
        
        # Сохранение данных
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_file = collector.save_data(data, f'devbot_metrika_data_{timestamp}.json')
        print(f"  ✓ Данные сохранены: {json_file.name}")
        
        try:
            excel_file = collector.export_to_excel(data, f'devbot_metrika_report_{timestamp}.xlsx')
            print(f"  ✓ Экспорт в Excel: {excel_file.name}")
        except Exception as e:
            print(f"  ⚠ Ошибка экспорта в Excel: {e}")
        
        # Анализ данных
        print("\n[5/5] Анализ данных...")
        try:
            analyzer = MetrikaAnalyzer()
            analysis = analyzer.analyze_data(data)
            
            summary = analysis.get('summary', {})
            print(f"✓ Анализ выполнен:")
            print(f"  - Счетчик: {summary.get('counter_name', 'N/A')}")
            print(f"  - Сайт: {summary.get('counter_site', 'N/A')}")
            
            traffic = analysis.get('traffic_analysis', {})
            if traffic:
                print(f"\n  Трафик за период:")
                print(f"  - Визитов: {traffic.get('total_visits', 0):.0f}")
                print(f"  - Просмотров: {traffic.get('total_pageviews', 0):.0f}")
                print(f"  - Пользователей: {traffic.get('total_users', 0):.0f}")
                print(f"  - Отказов: {traffic.get('bounce_rate', 0):.1f}%")
                print(f"  - Глубина просмотра: {traffic.get('avg_page_depth', 0):.2f}")
                print(f"  - Время на сайте: {traffic.get('avg_visit_duration', 0):.0f} сек")
            
            sources = analysis.get('sources_analysis', {})
            if sources:
                print(f"\n  Источники трафика:")
                top_sources = sources.get('top_sources', [])[:5]
                for i, source in enumerate(top_sources, 1):
                    source_name = source.get('source', 'N/A')
                    visits = source.get('visits', 0)
                    print(f"  {i}. {source_name}: {visits:.0f} визитов")
            
            # Рекомендации
            recommendations = analysis.get('recommendations', [])
            if recommendations:
                print(f"\n  Рекомендации ({len(recommendations)}):")
                for i, rec in enumerate(recommendations[:5], 1):
                    print(f"    {i}. {rec}")
            
            # Сохранение анализа
            analyzer.save_analysis(analysis, f'devbot_analysis_{timestamp}.json')
            print(f"\n  ✓ Анализ сохранен")
            
            try:
                analyzer.export_analysis_report(analysis, f'devbot_analysis_{timestamp}.xlsx')
                print(f"  ✓ Отчет экспортирован")
            except Exception as e:
                print(f"  ⚠ Ошибка экспорта отчета: {e}")
            
        except Exception as e:
            print(f"✗ Ошибка при анализе: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"✗ Ошибка при получении данных: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "="*70)
    print(" ✓ СТАТИСТИКА ПОЛУЧЕНА!")
    print("="*70)
    print("\nФайлы сохранены в:")
    print("  - data/ - исходные данные")
    print("  - reports/ - отчеты и анализ")


if __name__ == '__main__':
    main()

