"""
Пример использования коннектора Яндекс.Директ
"""
from connector import YandexDirectConnector
from data_collector import DataCollector
from analyzer import StrategyAnalyzer


def main():
    """Пример работы с коннектором"""
    
    # 1. Инициализация коннектора
    print("Инициализация коннектора...")
    connector = YandexDirectConnector()
    
    # 2. Получение информации о клиенте
    print("\nПолучение информации о клиенте...")
    client_info = connector.get_client_info()
    print(f"Логин: {client_info.get('Login', 'N/A')}")
    print(f"Валюта: {client_info.get('Currency', 'N/A')}")
    
    # 3. Получение списка кампаний
    print("\nПолучение списка кампаний...")
    campaigns = connector.get_campaigns()
    print(f"Найдено кампаний: {len(campaigns)}")
    
    if campaigns:
        for campaign in campaigns[:3]:
            print(f"  - {campaign.get('Name')} (ID: {campaign.get('Id')}, Статус: {campaign.get('Status')})")
    
    # 4. Сбор всех данных
    print("\nСбор всех данных...")
    collector = DataCollector(connector)
    data = collector.collect_all_data()
    
    print(f"Собрано:")
    print(f"  - Кампаний: {len(data.get('campaigns', []))}")
    print(f"  - Групп объявлений: {len(data.get('ad_groups', []))}")
    print(f"  - Объявлений: {len(data.get('ads', []))}")
    print(f"  - Ключевых слов: {len(data.get('keywords', []))}")
    
    # 5. Сохранение данных
    print("\nСохранение данных...")
    json_file = collector.save_data(data)
    print(f"Данные сохранены: {json_file.name}")
    
    # 6. Анализ стратегии
    print("\nАнализ стратегии...")
    analyzer = StrategyAnalyzer()
    analysis = analyzer.analyze_campaigns(data)
    
    summary = analysis.get('summary', {})
    print(f"\nРезультаты анализа:")
    print(f"  - Всего кампаний: {summary.get('total_campaigns', 0)}")
    print(f"  - Активных: {summary.get('active_campaigns', 0)}")
    print(f"  - Приостановленных: {summary.get('paused_campaigns', 0)}")
    
    # 7. Рекомендации
    recommendations = analysis.get('recommendations', [])
    if recommendations:
        print(f"\nРекомендации ({len(recommendations)}):")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"  {i}. {rec}")
    
    # 8. Сохранение анализа
    print("\nСохранение анализа...")
    analyzer.save_analysis(analysis)
    print("Анализ сохранен в reports/")


if __name__ == '__main__':
    main()

