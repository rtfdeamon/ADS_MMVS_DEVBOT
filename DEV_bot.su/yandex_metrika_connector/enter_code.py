#!/usr/bin/env python3
"""
Скрипт для ввода кода авторизации
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from oauth import YandexMetrikaOAuth

def main():
    print("\n" + "="*70)
    print(" ВВОД КОДА АВТОРИЗАЦИИ")
    print("="*70)
    print("\nПосле авторизации в браузере вы были перенаправлены на:")
    print("https://mmvs.ru/metrika?code=XXXXX")
    print("\nСкопируйте код из параметра 'code' из URL")
    print("(или вставьте полный URL с кодом)")
    print("\n" + "-"*70)
    
    code = input("\nВведите код авторизации (или полный URL): ").strip()
    
    if not code:
        print("\n✗ Код не введен")
        return
    
    oauth = YandexMetrikaOAuth()
    
    # Если введен полный URL, извлекаем код
    if code.startswith('http'):
        code = oauth.extract_code_from_url(code)
        if not code:
            print("\n✗ Не удалось извлечь код из URL")
            return
    
    print(f"\nПолучение токена по коду: {code[:10]}...")
    
    try:
        token_data = oauth.get_access_token(code)
        
        print("\n" + "="*70)
        print(" ✓ АВТОРИЗАЦИЯ УСПЕШНА!")
        print("="*70)
        print(f"\nAccess token: {token_data.get('access_token', 'N/A')[:30]}...")
        print(f"Токен сохранен в: {oauth.token_file}")
        print("\nТеперь вы можете запустить:")
        print("  python3 auto_test.py")
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"\n✗ Ошибка авторизации: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

