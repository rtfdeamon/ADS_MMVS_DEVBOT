"""
Тестовый скрипт для проверки работы коннектора Яндекс.Директ
"""
import sys
import logging
from pathlib import Path

# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, str(Path(__file__).parent))

from connector import YandexDirectConnector
from data_collector import DataCollector
from analyzer import StrategyAnalyzer
from config import YANDEX_DIRECT_TOKEN

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_connection():
    """Тест подключения к API"""
    print("\n" + "="*60)
    print("ТЕСТ 1: Проверка подключения к API Яндекс.Директ")
    print("="*60)
    
    try:
        connector = YandexDirectConnector()
        print("✓ Коннектор успешно инициализирован")
        
        # Получение информации о клиенте
        client_info = connector.get_client_info()
        if client_info:
            print(f"✓ Информация о клиенте получена:")
            print(f"  - Логин: {client_info.get('Login', 'N/A')}")
            print(f"  - Валюта: {client_info.get('Currency', 'N/A')}")
        else:
            print("⚠ Информация о клиенте не получена (возможно, требуется указать Client-Login)")
        
        return connector
        
    except Exception as e:
        print(f"✗ Ошибка подключения: {e}")
        return None


def test_get_campaigns(connector):
    """Тест получения кампаний"""
    print("\n" + "="*60)
    print("ТЕСТ 2: Получение списка кампаний")
    print("="*60)
    
    try:
        campaigns = connector.get_campaigns()
        
        if campaigns:
            print(f"✓ Получено кампаний: {len(campaigns)}")
            print("\nПервые 5 кампаний:")
            for i, campaign in enumerate(campaigns[:5], 1):
                print(f"  {i}. ID: {campaign.get('Id')}, "
                      f"Название: {campaign.get('Name', 'N/A')}, "
                      f"Статус: {campaign.get('Status', 'N/A')}")
        else:
            print("⚠ Кампании не найдены")
        
        return campaigns
        
    except Exception as e:
        print(f"✗ Ошибка получения кампаний: {e}")
        return []


def test_get_ad_groups(connector, campaign_ids):
    """Тест получения групп объявлений"""
    print("\n" + "="*60)
    print("ТЕСТ 3: Получение групп объявлений")
    print("="*60)
    
    if not campaign_ids:
        print("⚠ Нет кампаний для тестирования")
        return []
    
    try:
        ad_groups = connector.get_ad_groups(campaign_ids=campaign_ids[:3])
        
        if ad_groups:
            print(f"✓ Получено групп объявлений: {len(ad_groups)}")
            print("\nПервые 3 группы:")
            for i, ag in enumerate(ad_groups[:3], 1):
                print(f"  {i}. ID: {ag.get('Id')}, "
                      f"Название: {ag.get('Name', 'N/A')}, "
                      f"Кампания: {ag.get('CampaignId', 'N/A')}")
        else:
            print("⚠ Группы объявлений не найдены")
        
        return ad_groups
        
    except Exception as e:
        print(f"✗ Ошибка получения групп объявлений: {e}")
        return []


def test_get_ads(connector, campaign_ids):
    """Тест получения объявлений"""
    print("\n" + "="*60)
    print("ТЕСТ 4: Получение объявлений")
    print("="*60)
    
    if not campaign_ids:
        print("⚠ Нет кампаний для тестирования")
        return []
    
    try:
        ads = connector.get_ads(campaign_ids=campaign_ids[:3])
        
        if ads:
            print(f"✓ Получено объявлений: {len(ads)}")
            print("\nПервые 3 объявления:")
            for i, ad in enumerate(ads[:3], 1):
                ad_type = ad.get('Type', 'N/A')
                status = ad.get('Status', 'N/A')
                print(f"  {i}. ID: {ad.get('Id')}, "
                      f"Тип: {ad_type}, "
                      f"Статус: {status}")
        else:
            print("⚠ Объявления не найдены")
        
        return ads
        
    except Exception as e:
        print(f"✗ Ошибка получения объявлений: {e}")
        return []


def test_get_keywords(connector, campaign_ids):
    """Тест получения ключевых слов"""
    print("\n" + "="*60)
    print("ТЕСТ 5: Получение ключевых слов")
    print("="*60)
    
    if not campaign_ids:
        print("⚠ Нет кампаний для тестирования")
        return []
    
    try:
        keywords = connector.get_keywords(campaign_ids=campaign_ids[:3])
        
        if keywords:
            print(f"✓ Получено ключевых слов: {len(keywords)}")
            print("\nПервые 5 ключевых слов:")
            for i, kw in enumerate(keywords[:5], 1):
                keyword = kw.get('Keyword', 'N/A')
                bid = kw.get('Bid', 0)
                status = kw.get('Status', 'N/A')
                print(f"  {i}. {keyword} (ставка: {bid}, статус: {status})")
        else:
            print("⚠ Ключевые слова не найдены")
        
        return keywords
        
    except Exception as e:
        print(f"✗ Ошибка получения ключевых слов: {e}")
        return []


def test_data_collection(connector):
    """Тест сбора данных"""
    print("\n" + "="*60)
    print("ТЕСТ 6: Сбор всех данных")
    print("="*60)
    
    try:
        collector = DataCollector(connector)
        
        # Собираем данные
        data = collector.collect_all_data()
        
        print(f"✓ Данные собраны:")
        print(f"  - Кампаний: {len(data.get('campaigns', []))}")
        print(f"  - Групп объявлений: {len(data.get('ad_groups', []))}")
        print(f"  - Объявлений: {len(data.get('ads', []))}")
        print(f"  - Ключевых слов: {len(data.get('keywords', []))}")
        
        # Сохраняем данные
        json_file = collector.save_data(data)
        print(f"✓ Данные сохранены в JSON: {json_file.name}")
        
        # Экспортируем в Excel
        try:
            excel_file = collector.export_to_excel(data)
            print(f"✓ Данные экспортированы в Excel: {excel_file.name}")
        except ImportError:
            print("⚠ openpyxl не установлен, пропуск экспорта в Excel")
        
        return data
        
    except Exception as e:
        print(f"✗ Ошибка сбора данных: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_analysis(data):
    """Тест анализа данных"""
    print("\n" + "="*60)
    print("ТЕСТ 7: Анализ стратегии")
    print("="*60)
    
    if not data:
        print("⚠ Нет данных для анализа")
        return None
    
    try:
        analyzer = StrategyAnalyzer()
        
        # Выполняем анализ
        analysis = analyzer.analyze_campaigns(data)
        
        print("✓ Анализ выполнен:")
        summary = analysis.get('summary', {})
        print(f"  - Всего кампаний: {summary.get('total_campaigns', 0)}")
        print(f"  - Активных: {summary.get('active_campaigns', 0)}")
        print(f"  - Приостановленных: {summary.get('paused_campaigns', 0)}")
        print(f"  - Всего ключевых слов: {summary.get('total_keywords', 0)}")
        
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
        
        return analysis
        
    except Exception as e:
        print(f"✗ Ошибка анализа: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Основная функция тестирования"""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ КОННЕКТОРА ЯНДЕКС.ДИРЕКТ")
    print("="*60)
    
    if not YANDEX_DIRECT_TOKEN:
        print("\n✗ ОШИБКА: Токен Яндекс.Директ не найден!")
        print("   Укажите токен в файле config.txt или переменной окружения YANDEX_DIRECT_TOKEN")
        return
    
    # Тест 1: Подключение
    connector = test_connection()
    if not connector:
        print("\n✗ Не удалось подключиться к API. Проверьте токен и доступность API.")
        return
    
    # Тест 2: Получение кампаний
    campaigns = test_get_campaigns(connector)
    campaign_ids = [c['Id'] for c in campaigns] if campaigns else []
    
    # Тест 3: Группы объявлений
    ad_groups = test_get_ad_groups(connector, campaign_ids)
    
    # Тест 4: Объявления
    ads = test_get_ads(connector, campaign_ids)
    
    # Тест 5: Ключевые слова
    keywords = test_get_keywords(connector, campaign_ids)
    
    # Тест 6: Сбор данных
    data = test_data_collection(connector)
    
    # Тест 7: Анализ
    if data:
        analysis = test_analysis(data)
    
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("="*60)
    print("\nВсе файлы сохранены в папках:")
    print("  - data/ - исходные данные")
    print("  - reports/ - отчеты и анализ")


if __name__ == '__main__':
    main()

