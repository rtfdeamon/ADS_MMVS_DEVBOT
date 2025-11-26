#!/usr/bin/env python3
"""
Создание полной рекламной кампании в Яндекс.Директ "под ключ"
Кампания создается в статусе DRAFT (черновик) и не запускается автоматически
"""
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent))

from connector import YandexDirectConnector
from config import YANDEX_DIRECT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CampaignCreator:
    """Класс для создания рекламной кампании"""
    
    def __init__(self, connector: YandexDirectConnector):
        self.connector = connector
    
    def check_existing_campaigns(self) -> List[Dict]:
        """Проверка существующих кампаний"""
        try:
            campaigns = self.connector.get_campaigns()
            return campaigns
        except Exception as e:
            logger.error(f"Ошибка при проверке кампаний: {e}")
            return []
    
    def create_campaign(self, landing_url: str = "https://dev-bot.su") -> Dict:
        """
        Создание полной кампании
        
        Args:
            landing_url: URL посадочной страницы
            
        Returns:
            Созданная кампания
        """
        # Данные кампании
        campaign_data = {
            "Name": "Поиск | AI-решения | РФ",
            "StartDate": None,  # Не устанавливаем дату начала - кампания в черновике
            "DailyBudget": {
                "Amount": 1000000,  # 1000 руб в микро-валюте (копейки)
                "Currency": "RUB"
            },
            "TextCampaign": {
                "BiddingStrategy": {
                    "Search": {
                        "BiddingStrategyType": "HIGHEST_POSITION"
                    },
                    "Network": {
                        "BiddingStrategyType": "MAXIMUM_COVERAGE"
                    }
                },
                "Settings": [
                    {
                        "Option": "ENABLE_AREA_OF_INTEREST_TARGETING",
                        "Value": "YES"
                    },
                    {
                        "Option": "ENABLE_SITE_MONITORING",
                        "Value": "YES"
                    }
                ],
                "CounterIds": {
                    "Items": []  # Можно добавить ID счетчика Метрики
                },
                "RelevantKeywords": {
                    "BudgetPercent": 10,
                    "Mode": "MINIMUM_COST"
                },
                "Priority": "NORMAL"
            },
            "Settings": [
                {
                    "Option": "ENABLE_SITE_MONITORING",
                    "Value": "YES"
                },
                {
                    "Option": "ADD_METRICA_TAG",
                    "Value": "YES"
                }
            ],
            "NegativeKeywords": {
                "Items": [
                    "бесплатно",
                    "обучение",
                    "курсы",
                    "вакансия",
                    "скачать",
                    "реферат",
                    "своими руками",
                    "что это",
                    "статья",
                    "обзор",
                    "примеры",
                    "новости",
                    "книги",
                    "фильм",
                    "маск"
                ]
            },
            "NegativeKeywordSharedSetIds": {},
            "Geo": {
                "Items": [
                    1,   # Москва
                    2,   # Санкт-Петербург
                    54,  # Екатеринбург
                    43,  # Казань
                    65,  # Новосибирск
                    47   # Нижний Новгород
                ]
            },
            "Funds": {
                "Mode": "CAMPAIGN_BUDGET"
            },
            "Status": "DRAFT"  # Черновик - не запускается автоматически
        }
        
        # Создание кампании через API
        try:
            result = self.connector._make_request(
                'campaigns.add',
                {
                    'Campaigns': [campaign_data]
                }
            )
            
            if result.get('AddResults'):
                campaign_id = result['AddResults'][0].get('Id')
                logger.info(f"Кампания создана с ID: {campaign_id}")
                return {'Id': campaign_id, 'Name': campaign_data['Name']}
            else:
                raise Exception("Кампания не создана")
                
        except Exception as e:
            logger.error(f"Ошибка при создании кампании: {e}")
            raise
    
    def create_ad_groups(self, campaign_id: int, landing_url: str) -> List[Dict]:
        """Создание групп объявлений"""
        
        ad_groups_data = [
            {
                "Name": "Общий спрос на внедрение AI",
                "CampaignId": campaign_id,
                "NegativeKeywords": {
                    "Items": []
                },
                "NegativeKeywordSharedSetIds": {},
                "TrackingParams": "",
                "Settings": [],
                "Type": "TEXT_AD_GROUP",
                "Subtype": "NONE"
            },
            {
                "Name": "Спрос из Ритейла",
                "CampaignId": campaign_id,
                "NegativeKeywords": {
                    "Items": []
                },
                "NegativeKeywordSharedSetIds": {},
                "TrackingParams": "",
                "Settings": [],
                "Type": "TEXT_AD_GROUP",
                "Subtype": "NONE"
            },
            {
                "Name": "Спрос из Логистики",
                "CampaignId": campaign_id,
                "NegativeKeywords": {
                    "Items": []
                },
                "NegativeKeywordSharedSetIds": {},
                "TrackingParams": "",
                "Settings": [],
                "Type": "TEXT_AD_GROUP",
                "Subtype": "NONE"
            }
        ]
        
        try:
            result = self.connector._make_request(
                'adgroups.add',
                {
                    'AdGroups': ad_groups_data
                }
            )
            
            if result.get('AddResults'):
                ad_group_ids = [r.get('Id') for r in result['AddResults']]
                logger.info(f"Создано групп объявлений: {len(ad_group_ids)}")
                return [
                    {'Id': ad_group_ids[0], 'Name': 'Общий спрос на внедрение AI'},
                    {'Id': ad_group_ids[1], 'Name': 'Спрос из Ритейла'},
                    {'Id': ad_group_ids[2], 'Name': 'Спрос из Логистики'}
                ]
            else:
                raise Exception("Группы объявлений не созданы")
                
        except Exception as e:
            logger.error(f"Ошибка при создании групп: {e}")
            raise
    
    def create_keywords(self, ad_group_ids: List[int]) -> Dict:
        """Создание ключевых слов"""
        
        keywords_data = []
        
        # Группа 1: Общий спрос
        group1_keywords = [
            "внедрение ии в бизнес",
            "искусственный интеллект для бизнеса",
            "ai для бизнеса",
            "нейросети для бизнеса",
            "ии в бизнесе",
            "автоматизация бизнеса ии",
            "ии решения для бизнеса",
            "разработка ии решений",
            "заказать ai для бизнеса",
            "ai консалтинг",
            "интеграция искусственного интеллекта"
        ]
        
        for keyword in group1_keywords:
            keywords_data.append({
                "Keyword": keyword,
                "AdGroupId": ad_group_ids[0],
                "UserParam1": "",
                "UserParam2": ""
            })
        
        # Группа 2: Ритейл
        group2_keywords = [
            "искусственный интеллект в ритейле",
            "ai для прогнозирования спроса",
            "автоматизация склада для интернет-магазина",
            "компьютерное зрение для магазина",
            "ии для ритейла",
            "ai решения для розничной торговли"
        ]
        
        for keyword in group2_keywords:
            keywords_data.append({
                "Keyword": keyword,
                "AdGroupId": ad_group_ids[1],
                "UserParam1": "",
                "UserParam2": ""
            })
        
        # Группа 3: Логистика
        group3_keywords = [
            "ai для логистики",
            "оптимизация маршрутов доставки",
            "ии для управления запасами",
            "автоматизация цепей поставок",
            "ии в логистике",
            "ai оптимизация доставки"
        ]
        
        for keyword in group3_keywords:
            keywords_data.append({
                "Keyword": keyword,
                "AdGroupId": ad_group_ids[2],
                "UserParam1": "",
                "UserParam2": ""
            })
        
        try:
            result = self.connector._make_request(
                'keywords.add',
                {
                    'Keywords': keywords_data
                }
            )
            
            if result.get('AddResults'):
                added_count = len([r for r in result['AddResults'] if r.get('Id')])
                logger.info(f"Создано ключевых слов: {added_count}")
                return {'added': added_count, 'total': len(keywords_data)}
            else:
                raise Exception("Ключевые слова не созданы")
                
        except Exception as e:
            logger.error(f"Ошибка при создании ключевых слов: {e}")
            raise
    
    def create_ads(self, ad_group_ids: List[int], landing_url: str) -> Dict:
        """Создание объявлений"""
        
        ads_data = []
        
        # Объявление 1: Общий спрос
        ads_data.append({
            "AdGroupId": ad_group_ids[0],
            "Type": "TEXT_AD",
            "TextAd": {
                "Title": "Внедрение AI для вашего бизнеса",
                "Title2": "Окупаемость от 2 месяцев",
                "Text": "Готовые AI-решения для автоматизации рутины. Увеличим прибыль, сократим издержки. Бесплатная консультация!",
                "Href": landing_url,
                "DisplayUrlPath": "",
                "Mobile": "NO",
                "VCardId": None,
                "SitelinkSetId": None,
                "AdImageHash": None,
                "AdExtensionIds": None,
                "VideoExtensionId": None,
                "TurboPageId": None,
                "TurboPageModeration": None,
                "BusinessId": None,
                "Ppc": None,
                "AdImageModeration": None,
                "TextAdImageAdAction": None,
                "TextAdBuilderAd": None,
                "TextAdBuilderAdModeration": None
            }
        })
        
        # Объявление 2: Ритейл
        ads_data.append({
            "AdGroupId": ad_group_ids[1],
            "Type": "TEXT_AD",
            "TextAd": {
                "Title": "AI-решения для ритейла",
                "Title2": "Прогнозирование спроса",
                "Text": "Поможем сократить списания и избежать пустых полок. Готовые решения для ритейла. Узнайте больше!",
                "Href": f"{landing_url}/retail" if landing_url else landing_url,
                "DisplayUrlPath": "",
                "Mobile": "NO"
            }
        })
        
        # Объявление 3: Логистика
        ads_data.append({
            "AdGroupId": ad_group_ids[2],
            "Type": "TEXT_AD",
            "TextAd": {
                "Title": "AI для оптимизации логистики",
                "Title2": "Сокращение затрат на 20%",
                "Text": "Оптимизация маршрутов, управление запасами, прогнозирование. Готовые AI-решения. Рассчитайте экономию!",
                "Href": f"{landing_url}/logistics" if landing_url else landing_url,
                "DisplayUrlPath": "",
                "Mobile": "NO"
            }
        })
        
        try:
            result = self.connector._make_request(
                'ads.add',
                {
                    'Ads': ads_data
                }
            )
            
            if result.get('AddResults'):
                added_count = len([r for r in result['AddResults'] if r.get('Id')])
                logger.info(f"Создано объявлений: {added_count}")
                return {'added': added_count, 'total': len(ads_data)}
            else:
                raise Exception("Объявления не созданы")
                
        except Exception as e:
            logger.error(f"Ошибка при создании объявлений: {e}")
            raise


def main():
    """Основная функция"""
    print("\n" + "="*70)
    print(" СОЗДАНИЕ РЕКЛАМНОЙ КАМПАНИИ В ЯНДЕКС.ДИРЕКТ")
    print("="*70)
    
    if not YANDEX_DIRECT_TOKEN:
        print("\n✗ Токен Яндекс.Директ не найден!")
        print("Укажите токен в config.txt или переменной окружения YANDEX_DIRECT_TOKEN")
        return
    
    try:
        # Инициализация
        connector = YandexDirectConnector()
        creator = CampaignCreator(connector)
        
        # Проверка существующих кампаний
        print("\n[1/6] Проверка существующих кампаний...")
        existing_campaigns = creator.check_existing_campaigns()
        
        if existing_campaigns:
            print(f"✓ Найдено кампаний: {len(existing_campaigns)}")
            for camp in existing_campaigns[:3]:
                print(f"  - {camp.get('Name', 'N/A')} (ID: {camp.get('Id')}, Статус: {camp.get('Status', 'N/A')})")
            
            # Проверяем, есть ли уже наша кампания
            our_campaign = [c for c in existing_campaigns if 'AI-решения' in c.get('Name', '')]
            if our_campaign:
                print(f"\n✓ Кампания 'Поиск | AI-решения | РФ' уже существует!")
                print(f"  ID: {our_campaign[0].get('Id')}")
                print(f"  Статус: {our_campaign[0].get('Status', 'N/A')}")
                return
        
        # Создание кампании
        print("\n[2/6] Создание кампании...")
        landing_url = "https://dev-bot.su"  # Можно изменить
        campaign = creator.create_campaign(landing_url=landing_url)
        print(f"✓ Кампания создана: {campaign['Name']} (ID: {campaign['Id']})")
        
        # Создание групп объявлений
        print("\n[3/6] Создание групп объявлений...")
        ad_groups = creator.create_ad_groups(campaign['Id'], landing_url)
        print(f"✓ Создано групп: {len(ad_groups)}")
        for ag in ad_groups:
            print(f"  - {ag['Name']} (ID: {ag['Id']})")
        
        ad_group_ids = [ag['Id'] for ag in ad_groups]
        
        # Создание ключевых слов
        print("\n[4/6] Создание ключевых слов...")
        keywords_result = creator.create_keywords(ad_group_ids)
        print(f"✓ Создано ключевых слов: {keywords_result['added']}/{keywords_result['total']}")
        
        # Создание объявлений
        print("\n[5/6] Создание объявлений...")
        ads_result = creator.create_ads(ad_group_ids, landing_url)
        print(f"✓ Создано объявлений: {ads_result['added']}/{ads_result['total']}")
        
        # Итоги
        print("\n" + "="*70)
        print(" ✓ КАМПАНИЯ СОЗДАНА УСПЕШНО!")
        print("="*70)
        print(f"\nКампания: {campaign['Name']}")
        print(f"ID кампании: {campaign['Id']}")
        print(f"Статус: DRAFT (черновик - не запущена)")
        print(f"\nСоздано:")
        print(f"  - Групп объявлений: {len(ad_groups)}")
        print(f"  - Ключевых слов: {keywords_result['added']}")
        print(f"  - Объявлений: {ads_result['added']}")
        print(f"\n⚠️  ВАЖНО: Кампания создана в статусе DRAFT (черновик)")
        print("   Она не будет запущена автоматически.")
        print("   Для запуска перейдите в интерфейс Яндекс.Директ и активируйте кампанию.")
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

