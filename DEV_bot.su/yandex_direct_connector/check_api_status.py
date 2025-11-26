#!/usr/bin/env python3
"""
Диагностика проблем с API Яндекс.Директ
"""
import sys
import requests
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import YANDEX_DIRECT_TOKEN, API_URL

def check_api_status():
    """Проверка статуса API"""
    print("\n" + "="*70)
    print(" ДИАГНОСТИКА API ЯНДЕКС.ДИРЕКТ")
    print("="*70)
    
    # 1. Проверка токена
    print("\n[1] Проверка токена...")
    if not YANDEX_DIRECT_TOKEN:
        print("✗ Токен не найден!")
        return
    print(f"✓ Токен найден (длина: {len(YANDEX_DIRECT_TOKEN)} символов)")
    print(f"  Начинается с: {YANDEX_DIRECT_TOKEN[:15]}...")
    
    # 2. Проверка доступности сервера
    print("\n[2] Проверка доступности сервера...")
    try:
        response = requests.get('https://api.direct.yandex.com', timeout=5)
        print(f"✓ Сервер доступен (статус: {response.status_code})")
    except Exception as e:
        print(f"✗ Сервер недоступен: {e}")
        return
    
    # 3. Проверка версии API
    print("\n[3] Проверка версии API...")
    print(f"  URL: {API_URL}")
    print("  Версия: v5 (текущая)")
    
    # 4. Тестовый запрос
    print("\n[4] Тестовый запрос к API...")
    headers = {
        'Authorization': f'Bearer {YANDEX_DIRECT_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    body = {
        'method': 'campaigns.get',
        'params': {
            'SelectionCriteria': {},
            'FieldNames': ['Id', 'Name']
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=body, timeout=10)
        print(f"  HTTP статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'error' in data:
                error = data['error']
                error_code = error.get('error_code', 'N/A')
                error_string = error.get('error_string', 'N/A')
                error_detail = error.get('error_detail', '')
                
                print(f"\n✗ Ошибка API:")
                print(f"  Код: {error_code}")
                print(f"  Сообщение: {error_string}")
                if error_detail:
                    print(f"  Детали: {error_detail}")
                
                # Анализ ошибки
                print(f"\n📋 АНАЛИЗ ОШИБКИ:")
                
                if error_code == 1000:
                    print("  Ошибка 1000: 'Сервер временно недоступен'")
                    print("\n  Возможные причины:")
                    print("  1. Временные технические работы на стороне Яндекс.Директ")
                    print("  2. Проблемы с конкретным аккаунтом (требуется верификация)")
                    print("  3. Токен устарел или невалиден")
                    print("  4. Превышен лимит запросов")
                    print("  5. Аккаунт требует дополнительной настройки")
                    print("\n  Рекомендации:")
                    print("  • Подождите 10-15 минут и повторите запрос")
                    print("  • Проверьте статус сервисов Яндекс: https://status.yandex.ru/")
                    print("  • Проверьте аккаунт в интерфейсе Яндекс.Директ")
                    print("  • Убедитесь, что аккаунт верифицирован")
                    print("  • При необходимости обновите токен")
                
                elif error_code == 152:
                    print("  Ошибка 152: 'Неверный токен'")
                    print("  Решение: Обновите токен доступа")
                
                elif error_code == 53:
                    print("  Ошибка 53: 'Доступ запрещен'")
                    print("  Решение: Проверьте права доступа токена")
                
            else:
                print("✓ API работает корректно!")
                if 'result' in data:
                    campaigns = data['result'].get('Campaigns', [])
                    print(f"  Найдено кампаний: {len(campaigns)}")
        
        else:
            print(f"✗ HTTP ошибка: {response.status_code}")
            print(f"  Ответ: {response.text[:200]}")
    
    except requests.exceptions.Timeout:
        print("✗ Таймаут запроса")
    except requests.exceptions.RequestException as e:
        print(f"✗ Ошибка запроса: {e}")
    except Exception as e:
        print(f"✗ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Проверка альтернативных методов
    print("\n[5] Проверка альтернативных методов...")
    print("  Пробую метод clients.get (более простой)...")
    
    body2 = {
        'method': 'clients.get',
        'params': {
            'FieldNames': ['Login']
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=body2, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'error' in data:
                error_code = data['error'].get('error_code')
                if error_code == 1000:
                    print("  ✗ Та же ошибка 1000")
                    print("  Вывод: Проблема глобальная, не связана с конкретным методом")
                else:
                    print(f"  Другая ошибка: {error_code}")
            else:
                print("  ✓ Метод clients.get работает!")
        else:
            print(f"  HTTP ошибка: {response.status_code}")
    except Exception as e:
        print(f"  Ошибка: {e}")
    
    print("\n" + "="*70)
    print(" ДИАГНОСТИКА ЗАВЕРШЕНА")
    print("="*70)
    
    print("\n💡 СЛЕДУЮЩИЕ ШАГИ:")
    print("1. Проверьте статус сервисов: https://status.yandex.ru/")
    print("2. Зайдите в интерфейс Яндекс.Директ и проверьте аккаунт")
    print("3. Убедитесь, что аккаунт верифицирован")
    print("4. Попробуйте создать кампанию через веб-интерфейс")
    print("5. Если проблема сохраняется - обратитесь в поддержку Яндекс.Директ")


if __name__ == '__main__':
    check_api_status()

