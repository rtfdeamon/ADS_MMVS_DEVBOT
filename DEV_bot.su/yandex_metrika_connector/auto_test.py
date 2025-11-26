#!/usr/bin/env python3
"""
Автоматический тест коннектора Яндекс.Метрика
Работает с токеном из переменной окружения или файла
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from oauth import YandexMetrikaOAuth
from connector import YandexMetrikaConnector
from data_collector import MetrikaDataCollector
from analyzer import MetrikaAnalyzer


def get_token():
    """Получение токена из различных источников"""
    # 1. Из переменной окружения
    token = os.getenv('YANDEX_METRIKA_TOKEN', '')
    if token:
        print("✓ Токен найден в переменной окружения")
        return token
    
    # 2. Из файла
    oauth = YandexMetrikaOAuth()
    token_data = oauth.load_token()
    if token_data and token_data.get('access_token'):
        print("✓ Токен найден в файле")
        return token_data.get('access_token')
    
    # 3. Генерируем URL для авторизации
    print("⚠ Токен не найден")
    print("\nДля получения токена:")
    print("1. Перейдите по ссылке:")
    auth_url = oauth.get_authorization_url()
    print(f"   {auth_url}")
    print("\n2. После авторизации вы будете перенаправлены на:")
    print(f"   https://mmvs.ru/metrika?code=XXXXX")
    print("\n3. Скопируйте код из URL и выполните:")
    print("   export YANDEX_METRIKA_TOKEN='ваш_токен'")
    print("   или запустите: python3 oauth.py")
    
    return None


def run_tests(token):
    """Запуск тестов"""
    print("\n" + "="*70)
    print(" ЗАПУСК ТЕСТОВ")
    print("="*70)
    
    results = {
        'connection': False,
        'counters': False,
        'data_collection': False,
        'analysis': False
    }
    
    # Тест 1: Подключение
    print("\n[Тест 1] Подключение к API...")
    try:
        connector = YandexMetrikaConnector(token=token)
        print("✓ Подключение успешно")
        results['connection'] = True
    except Exception as e:
        print(f"✗ Ошибка подключения: {e}")
        return results
    
    # Тест 2: Получение счетчиков
    print("\n[Тест 2] Получение счетчиков...")
    try:
        counters = connector.get_counters()
        if counters:
            print(f"✓ Получено счетчиков: {len(counters)}")
            for i, counter in enumerate(counters[:3], 1):
                print(f"  {i}. {counter.get('name', 'N/A')} (ID: {counter.get('id')})")
            results['counters'] = True
            counter_id = counters[0]['id']
        else:
            print("⚠ Счетчики не найдены")
            return results
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return results
    
    # Тест 3: Сбор данных
    print("\n[Тест 3] Сбор данных...")
    try:
        collector = MetrikaDataCollector(connector)
        data = collector.collect_all_data(counter_id=counter_id)
        
        print(f"✓ Данные собраны:")
        print(f"  - Целей: {len(data.get('goals', []))}")
        print(f"  - Фильтров: {len(data.get('filters', []))}")
        
        visits_data = data.get('visits_report', {}).get('data', [])
        print(f"  - Записей в отчете о визитах: {len(visits_data)}")
        
        # Сохранение
        json_file = collector.save_data(data)
        print(f"✓ Данные сохранены: {json_file.name}")
        
        try:
            excel_file = collector.export_to_excel(data)
            print(f"✓ Экспорт в Excel: {excel_file.name}")
        except Exception as e:
            print(f"⚠ Ошибка экспорта в Excel: {e}")
        
        results['data_collection'] = True
        
    except Exception as e:
        print(f"✗ Ошибка сбора данных: {e}")
        import traceback
        traceback.print_exc()
        return results
    
    # Тест 4: Анализ
    print("\n[Тест 4] Анализ данных...")
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
        
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            print(f"\n  Рекомендации ({len(recommendations)}):")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"    {i}. {rec}")
        
        analyzer.save_analysis(analysis)
        print(f"✓ Анализ сохранен")
        
        try:
            analyzer.export_analysis_report(analysis)
            print(f"✓ Отчет экспортирован")
        except Exception as e:
            print(f"⚠ Ошибка экспорта отчета: {e}")
        
        results['analysis'] = True
        
    except Exception as e:
        print(f"✗ Ошибка анализа: {e}")
        import traceback
        traceback.print_exc()
        return results
    
    return results


def main():
    """Основная функция"""
    print("\n" + "="*70)
    print(" АВТОМАТИЧЕСКИЙ ТЕСТ КОННЕКТОРА ЯНДЕКС.МЕТРИКА")
    print("="*70)
    
    # Получаем токен
    token = get_token()
    
    if not token:
        print("\n" + "="*70)
        print(" ТОКЕН НЕ НАЙДЕН")
        print("="*70)
        print("\nДля продолжения:")
        print("1. Установите переменную окружения:")
        print("   export YANDEX_METRIKA_TOKEN='ваш_токен'")
        print("\n2. Или запустите интерактивную авторизацию:")
        print("   python3 oauth.py")
        print("\n3. Затем запустите этот скрипт снова:")
        print("   python3 auto_test.py")
        return
    
    # Запускаем тесты
    results = run_tests(token)
    
    # Итоги
    print("\n" + "="*70)
    print(" РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("="*70)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "✓" if result else "✗"
        print(f"  {status} {test_name}")
    
    print(f"\nПройдено тестов: {passed}/{total}")
    
    if passed == total:
        print("\n✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("\nФайлы сохранены в:")
        print("  - data/ - исходные данные")
        print("  - reports/ - отчеты и анализ")
    else:
        print("\n⚠ Некоторые тесты не пройдены. Проверьте логи выше.")


if __name__ == '__main__':
    main()

