"""
Тестовый скрипт для проверки работы коннектора Яндекс.Метрика
"""
import sys
import logging
from pathlib import Path

# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, str(Path(__file__).parent))

from oauth import YandexMetrikaOAuth, interactive_authorization
from connector import YandexMetrikaConnector
from data_collector import MetrikaDataCollector
from analyzer import MetrikaAnalyzer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_oauth():
    """Тест OAuth авторизации"""
    print("\n" + "="*60)
    print("ТЕСТ 1: Проверка OAuth авторизации")
    print("="*60)
    
    try:
        oauth = YandexMetrikaOAuth()
        
        # Проверяем наличие сохраненного токена
        token_data = oauth.load_token()
        
        if token_data and token_data.get('access_token'):
            print("✓ Токен найден в файле")
            print(f"  Access token: {token_data.get('access_token', 'N/A')[:20]}...")
            return token_data.get('access_token')
        else:
            print("⚠ Токен не найден. Требуется авторизация.")
            print("\nЗапустите авторизацию? (y/n): ", end='')
            response = input().strip().lower()
            
            if response == 'y':
                token_data = interactive_authorization()
                if token_data:
                    return token_data.get('access_token')
            else:
                print("Пропуск авторизации. Используйте oauth.py для получения токена.")
                return None
                
    except Exception as e:
        print(f"✗ Ошибка OAuth: {e}")
        return None


def test_connection(token):
    """Тест подключения к API"""
    print("\n" + "="*60)
    print("ТЕСТ 2: Проверка подключения к API Яндекс.Метрика")
    print("="*60)
    
    if not token:
        print("⚠ Токен не предоставлен, пропуск теста")
        return None
    
    try:
        connector = YandexMetrikaConnector(token=token)
        print("✓ Коннектор успешно инициализирован")
        return connector
        
    except Exception as e:
        print(f"✗ Ошибка подключения: {e}")
        return None


def test_get_counters(connector):
    """Тест получения счетчиков"""
    print("\n" + "="*60)
    print("ТЕСТ 3: Получение списка счетчиков")
    print("="*60)
    
    if not connector:
        print("⚠ Коннектор не инициализирован, пропуск теста")
        return []
    
    try:
        counters = connector.get_counters()
        
        if counters:
            print(f"✓ Получено счетчиков: {len(counters)}")
            print("\nСписок счетчиков:")
            for i, counter in enumerate(counters[:5], 1):
                print(f"  {i}. ID: {counter.get('id')}, "
                      f"Название: {counter.get('name', 'N/A')}, "
                      f"Сайт: {counter.get('site', 'N/A')}")
        else:
            print("⚠ Счетчики не найдены")
        
        return counters
        
    except Exception as e:
        print(f"✗ Ошибка получения счетчиков: {e}")
        import traceback
        traceback.print_exc()
        return []


def test_get_counter_info(connector, counter_id):
    """Тест получения информации о счетчике"""
    print("\n" + "="*60)
    print("ТЕСТ 4: Получение информации о счетчике")
    print("="*60)
    
    if not connector or not counter_id:
        print("⚠ Нет данных для тестирования")
        return {}
    
    try:
        counter_info = connector.get_counter_info(counter_id)
        
        if counter_info:
            print("✓ Информация о счетчике получена:")
            print(f"  - Название: {counter_info.get('name', 'N/A')}")
            print(f"  - Сайт: {counter_info.get('site', 'N/A')}")
            print(f"  - Статус: {counter_info.get('status', 'N/A')}")
            print(f"  - Тип: {counter_info.get('type', 'N/A')}")
        else:
            print("⚠ Информация о счетчике не получена")
        
        return counter_info
        
    except Exception as e:
        print(f"✗ Ошибка получения информации: {e}")
        return {}


def test_get_goals(connector, counter_id):
    """Тест получения целей"""
    print("\n" + "="*60)
    print("ТЕСТ 5: Получение целей счетчика")
    print("="*60)
    
    if not connector or not counter_id:
        print("⚠ Нет данных для тестирования")
        return []
    
    try:
        goals = connector.get_goals(counter_id)
        
        if goals:
            print(f"✓ Получено целей: {len(goals)}")
            print("\nПервые 5 целей:")
            for i, goal in enumerate(goals[:5], 1):
                print(f"  {i}. ID: {goal.get('id')}, "
                      f"Название: {goal.get('name', 'N/A')}, "
                      f"Тип: {goal.get('type', 'N/A')}")
        else:
            print("⚠ Цели не найдены")
        
        return goals
        
    except Exception as e:
        print(f"✗ Ошибка получения целей: {e}")
        return []


def test_get_reports(connector, counter_id):
    """Тест получения отчетов"""
    print("\n" + "="*60)
    print("ТЕСТ 6: Получение отчетов")
    print("="*60)
    
    if not connector or not counter_id:
        print("⚠ Нет данных для тестирования")
        return {}
    
    try:
        reports = {}
        
        # Отчет о визитах
        print("\nПолучение отчета о визитах...")
        visits_report = connector.get_visits_report(counter_id)
        reports['visits'] = visits_report
        if visits_report.get('data'):
            print(f"✓ Получено записей: {len(visits_report['data'])}")
        else:
            print("⚠ Данные не получены")
        
        # Отчет по источникам
        print("\nПолучение отчета по источникам...")
        sources_report = connector.get_sources_report(counter_id)
        reports['sources'] = sources_report
        if sources_report.get('data'):
            print(f"✓ Получено записей: {len(sources_report['data'])}")
        else:
            print("⚠ Данные не получены")
        
        # Отчет по страницам
        print("\nПолучение отчета по страницам...")
        pages_report = connector.get_pages_report(counter_id)
        reports['pages'] = pages_report
        if pages_report.get('data'):
            print(f"✓ Получено записей: {len(pages_report['data'])}")
        else:
            print("⚠ Данные не получены")
        
        return reports
        
    except Exception as e:
        print(f"✗ Ошибка получения отчетов: {e}")
        import traceback
        traceback.print_exc()
        return {}


def test_data_collection(connector, counter_id):
    """Тест сбора данных"""
    print("\n" + "="*60)
    print("ТЕСТ 7: Сбор всех данных")
    print("="*60)
    
    if not connector:
        print("⚠ Коннектор не инициализирован")
        return None
    
    try:
        collector = MetrikaDataCollector(connector)
        
        # Собираем данные
        data = collector.collect_all_data(counter_id=counter_id)
        
        print(f"✓ Данные собраны:")
        print(f"  - Счетчиков: {len(data.get('counters', []))}")
        print(f"  - Целей: {len(data.get('goals', []))}")
        print(f"  - Фильтров: {len(data.get('filters', []))}")
        
        visits_data = data.get('visits_report', {}).get('data', [])
        print(f"  - Записей в отчете о визитах: {len(visits_data)}")
        
        # Сохраняем данные
        json_file = collector.save_data(data)
        print(f"✓ Данные сохранены в JSON: {json_file.name}")
        
        # Экспортируем в Excel
        try:
            excel_file = collector.export_to_excel(data)
            print(f"✓ Данные экспортированы в Excel: {excel_file.name}")
        except ImportError:
            print("⚠ openpyxl не установлен, пропуск экспорта в Excel")
        except Exception as e:
            print(f"⚠ Ошибка экспорта в Excel: {e}")
        
        return data
        
    except Exception as e:
        print(f"✗ Ошибка сбора данных: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_analysis(data):
    """Тест анализа данных"""
    print("\n" + "="*60)
    print("ТЕСТ 8: Анализ данных")
    print("="*60)
    
    if not data:
        print("⚠ Нет данных для анализа")
        return None
    
    try:
        analyzer = MetrikaAnalyzer()
        
        # Выполняем анализ
        analysis = analyzer.analyze_data(data)
        
        print("✓ Анализ выполнен:")
        summary = analysis.get('summary', {})
        print(f"  - Счетчик: {summary.get('counter_name', 'N/A')}")
        print(f"  - Сайт: {summary.get('counter_site', 'N/A')}")
        print(f"  - Целей: {summary.get('total_goals', 0)}")
        
        traffic = analysis.get('traffic_analysis', {})
        if traffic:
            print(f"  - Всего визитов: {traffic.get('total_visits', 0):.0f}")
            print(f"  - Всего просмотров: {traffic.get('total_pageviews', 0):.0f}")
            print(f"  - Всего пользователей: {traffic.get('total_users', 0):.0f}")
        
        # Рекомендации
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            print(f"\n✓ Сгенерировано рекомендаций: {len(recommendations)}")
            print("\nРекомендации:")
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"  {i}. {rec}")
        
        # Сохраняем анализ
        json_file = analyzer.save_analysis(analysis)
        print(f"\n✓ Анализ сохранен в JSON: {json_file.name}")
        
        # Экспортируем отчет
        try:
            excel_file = analyzer.export_analysis_report(analysis)
            print(f"✓ Отчет экспортирован в Excel: {excel_file.name}")
        except ImportError:
            print("⚠ openpyxl не установлен, пропуск экспорта в Excel")
        except Exception as e:
            print(f"⚠ Ошибка экспорта в Excel: {e}")
        
        return analysis
        
    except Exception as e:
        print(f"✗ Ошибка анализа: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Основная функция тестирования"""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ КОННЕКТОРА ЯНДЕКС.МЕТРИКА")
    print("="*60)
    
    # Тест 1: OAuth
    token = test_oauth()
    
    if not token:
        print("\n⚠ Для продолжения тестирования требуется токен доступа.")
        print("Запустите: python3 oauth.py")
        return
    
    # Тест 2: Подключение
    connector = test_connection(token)
    if not connector:
        print("\n✗ Не удалось подключиться к API.")
        return
    
    # Тест 3: Получение счетчиков
    counters = test_get_counters(connector)
    counter_id = counters[0]['id'] if counters else None
    
    if not counter_id:
        print("\n⚠ Нет доступных счетчиков для тестирования.")
        return
    
    # Тест 4: Информация о счетчике
    counter_info = test_get_counter_info(connector, counter_id)
    
    # Тест 5: Цели
    goals = test_get_goals(connector, counter_id)
    
    # Тест 6: Отчеты
    reports = test_get_reports(connector, counter_id)
    
    # Тест 7: Сбор данных
    data = test_data_collection(connector, counter_id)
    
    # Тест 8: Анализ
    if data:
        analysis = test_analysis(data)
    
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("="*60)
    print("\nВсе файлы сохранены в папках:")
    print("  - data/ - исходные данные")
    print("  - reports/ - отчеты и анализ")
    print("  - tokens/ - токены доступа")


if __name__ == '__main__':
    main()

