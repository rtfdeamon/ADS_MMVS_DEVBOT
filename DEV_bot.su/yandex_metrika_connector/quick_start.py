#!/usr/bin/env python3
"""
Быстрый старт для коннектора Яндекс.Метрика
Автоматически проверяет наличие токена и запускает тесты
"""
import sys
import os
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from oauth import YandexMetrikaOAuth, interactive_authorization
from connector import YandexMetrikaConnector
from data_collector import MetrikaDataCollector
from analyzer import MetrikaAnalyzer


def check_token():
    """Проверка наличия токена"""
    oauth = YandexMetrikaOAuth()
    token_data = oauth.load_token()
    
    if token_data and token_data.get('access_token'):
        return token_data.get('access_token')
    return None


def main():
    """Основная функция"""
    print("\n" + "="*70)
    print(" БЫСТРЫЙ СТАРТ КОННЕКТОРА ЯНДЕКС.МЕТРИКА")
    print("="*70)
    
    # Проверяем токен
    print("\n[1/4] Проверка токена доступа...")
    token = check_token()
    
    if not token:
        print("⚠ Токен не найден. Запуск авторизации...")
        print("\n" + "-"*70)
        token_data = interactive_authorization()
        
        if not token_data:
            print("\n✗ Авторизация не завершена. Запустите скрипт снова.")
            return
        
        token = token_data.get('access_token')
        print("\n✓ Токен получен!")
    else:
        print("✓ Токен найден")
    
    # Инициализация коннектора
    print("\n[2/4] Инициализация коннектора...")
    try:
        connector = YandexMetrikaConnector(token=token)
        print("✓ Коннектор инициализирован")
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return
    
    # Получение счетчиков
    print("\n[3/4] Получение данных...")
    try:
        counters = connector.get_counters()
        
        if not counters:
            print("⚠ Счетчики не найдены")
            return
        
        print(f"✓ Найдено счетчиков: {len(counters)}")
        counter_id = counters[0]['id']
        print(f"  Используется счетчик: {counters[0].get('name', 'N/A')} (ID: {counter_id})")
        
        # Сбор данных
        print("\n  Сбор данных о счетчике...")
        collector = MetrikaDataCollector(connector)
        data = collector.collect_all_data(counter_id=counter_id)
        
        print(f"  ✓ Данные собраны:")
        print(f"    - Целей: {len(data.get('goals', []))}")
        print(f"    - Фильтров: {len(data.get('filters', []))}")
        
        visits_data = data.get('visits_report', {}).get('data', [])
        print(f"    - Записей в отчете о визитах: {len(visits_data)}")
        
        # Сохранение данных
        json_file = collector.save_data(data)
        print(f"  ✓ Данные сохранены: {json_file.name}")
        
        try:
            excel_file = collector.export_to_excel(data)
            print(f"  ✓ Экспорт в Excel: {excel_file.name}")
        except Exception as e:
            print(f"  ⚠ Ошибка экспорта в Excel: {e}")
        
    except Exception as e:
        print(f"✗ Ошибка при получении данных: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Анализ данных
    print("\n[4/4] Анализ данных...")
    try:
        analyzer = MetrikaAnalyzer()
        analysis = analyzer.analyze_data(data)
        
        summary = analysis.get('summary', {})
        print(f"✓ Анализ выполнен:")
        print(f"  - Счетчик: {summary.get('counter_name', 'N/A')}")
        print(f"  - Сайт: {summary.get('counter_site', 'N/A')}")
        
        traffic = analysis.get('traffic_analysis', {})
        if traffic:
            print(f"  - Визитов: {traffic.get('total_visits', 0):.0f}")
            print(f"  - Просмотров: {traffic.get('total_pageviews', 0):.0f}")
            print(f"  - Пользователей: {traffic.get('total_users', 0):.0f}")
        
        # Рекомендации
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            print(f"\n  Рекомендации ({len(recommendations)}):")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"    {i}. {rec}")
        
        # Сохранение анализа
        analyzer.save_analysis(analysis)
        print(f"  ✓ Анализ сохранен")
        
        try:
            analyzer.export_analysis_report(analysis)
            print(f"  ✓ Отчет экспортирован")
        except Exception as e:
            print(f"  ⚠ Ошибка экспорта отчета: {e}")
        
    except Exception as e:
        print(f"✗ Ошибка при анализе: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "="*70)
    print(" ✓ ВСЕ ГОТОВО!")
    print("="*70)
    print("\nФайлы сохранены в:")
    print("  - data/ - исходные данные")
    print("  - reports/ - отчеты и анализ")
    print("\nДля повторного запуска просто выполните:")
    print("  python3 quick_start.py")


if __name__ == '__main__':
    main()

