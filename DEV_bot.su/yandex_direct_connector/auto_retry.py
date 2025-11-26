#!/usr/bin/env python3
"""
Автоматическая проверка доступности API и создание кампании
Будет пытаться создать кампанию каждые 5 минут до успеха
"""
import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from connector import YandexDirectConnector
from create_campaign import CampaignCreator

def check_and_create(max_attempts=12, interval=300):
    """
    Проверка API и создание кампании
    
    Args:
        max_attempts: Максимальное количество попыток
        interval: Интервал между попытками в секундах (по умолчанию 5 минут)
    """
    print("\n" + "="*70)
    print(" АВТОМАТИЧЕСКАЯ ПРОВЕРКА API И СОЗДАНИЕ КАМПАНИИ")
    print("="*70)
    print(f"\nБуду проверять API каждые {interval//60} минут")
    print(f"Максимум попыток: {max_attempts}")
    print(f"Общее время ожидания: до {max_attempts * interval // 60} минут")
    print("\nНажмите Ctrl+C для остановки\n")
    
    connector = None
    creator = None
    
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"\n[{attempt}/{max_attempts}] Попытка {attempt} - {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 70)
            
            # Инициализация
            if not connector:
                connector = YandexDirectConnector()
                creator = CampaignCreator(connector)
            
            # Проверка доступности API
            print("Проверка доступности API...")
            campaigns = creator.check_existing_campaigns()
            
            # Если проверка прошла успешно
            if campaigns is not None:
                print("✓ API доступен!")
                
                # Проверяем, есть ли уже наша кампания
                our_campaign = [c for c in campaigns if 'AI-решения' in c.get('Name', '')]
                if our_campaign:
                    print(f"\n✓ Кампания 'Поиск | AI-решения | РФ' уже существует!")
                    print(f"  ID: {our_campaign[0].get('Id')}")
                    print(f"  Статус: {our_campaign[0].get('Status', 'N/A')}")
                    return True
                
                # Создаем кампанию
                print("\nСоздание кампании...")
                landing_url = "https://dev-bot.su"
                campaign = creator.create_campaign(landing_url=landing_url)
                print(f"✓ Кампания создана: {campaign['Name']} (ID: {campaign['Id']})")
                
                # Создаем группы
                print("\nСоздание групп объявлений...")
                ad_groups = creator.create_ad_groups(campaign['Id'], landing_url)
                print(f"✓ Создано групп: {len(ad_groups)}")
                
                ad_group_ids = [ag['Id'] for ag in ad_groups]
                
                # Создаем ключевые слова
                print("\nСоздание ключевых слов...")
                keywords_result = creator.create_keywords(ad_group_ids)
                print(f"✓ Создано ключевых слов: {keywords_result['added']}/{keywords_result['total']}")
                
                # Создаем объявления
                print("\nСоздание объявлений...")
                ads_result = creator.create_ads(ad_group_ids, landing_url)
                print(f"✓ Создано объявлений: {ads_result['added']}/{ads_result['total']}")
                
                print("\n" + "="*70)
                print(" ✓ КАМПАНИЯ УСПЕШНО СОЗДАНА!")
                print("="*70)
                print(f"\nКампания: {campaign['Name']}")
                print(f"ID: {campaign['Id']}")
                print(f"Статус: DRAFT (черновик)")
                print("\n⚠️  ВАЖНО: Кампания создана в статусе DRAFT")
                print("   Она не будет запущена автоматически.")
                print("   Для запуска перейдите в интерфейс Яндекс.Директ.")
                
                return True
            
        except Exception as e:
            error_msg = str(e)
            if '1000' in error_msg or 'Сервер временно недоступен' in error_msg:
                print(f"✗ API все еще недоступен (ошибка 1000)")
                if attempt < max_attempts:
                    wait_time = interval
                    print(f"⏳ Ожидание {wait_time//60} минут до следующей попытки...")
                    print(f"   Следующая попытка в: {(datetime.now().timestamp() + wait_time):%H:%M:%S}")
                    time.sleep(wait_time)
                else:
                    print(f"\n✗ Достигнут лимит попыток ({max_attempts})")
                    print("API все еще недоступен.")
                    print("\nРекомендации:")
                    print("1. Проверьте статус сервисов: https://status.yandex.ru/")
                    print("2. Создайте кампанию вручную: см. manual_campaign_guide.md")
                    print("3. Попробуйте позже")
                    return False
            else:
                print(f"✗ Ошибка: {e}")
                import traceback
                traceback.print_exc()
                return False
    
    return False


if __name__ == '__main__':
    try:
        success = check_and_create(max_attempts=12, interval=300)  # 12 попыток по 5 минут = 1 час
        if success:
            print("\n✓ Готово!")
        else:
            print("\n⚠️  Кампания не создана. Используйте manual_campaign_guide.md для ручного создания.")
    except KeyboardInterrupt:
        print("\n\nОстановлено пользователем")
    except Exception as e:
        print(f"\n✗ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()


