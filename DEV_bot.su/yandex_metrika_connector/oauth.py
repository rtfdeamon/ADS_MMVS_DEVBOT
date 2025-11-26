"""
Модуль для OAuth авторизации в Яндекс.Метрика
"""
import json
import logging
import webbrowser
from pathlib import Path
from typing import Optional, Dict
import requests
from urllib.parse import urlencode, parse_qs, urlparse

from config import (
    OAUTH_CLIENT_ID,
    OAUTH_CLIENT_SECRET,
    OAUTH_REDIRECT_URI,
    OAUTH_AUTHORIZE_URL,
    OAUTH_TOKEN_URL,
    TOKENS_DIR,
    LOG_FORMAT,
    LOG_FILE
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class YandexMetrikaOAuth:
    """Класс для OAuth авторизации в Яндекс.Метрика"""
    
    def __init__(self, client_id: Optional[str] = None, 
                 client_secret: Optional[str] = None,
                 redirect_uri: Optional[str] = None):
        """
        Инициализация OAuth клиента
        
        Args:
            client_id: Client ID приложения
            client_secret: Client Secret приложения
            redirect_uri: Redirect URI
        """
        self.client_id = client_id or OAUTH_CLIENT_ID
        self.client_secret = client_secret or OAUTH_CLIENT_SECRET
        self.redirect_uri = redirect_uri or OAUTH_REDIRECT_URI
        self.token_file = TOKENS_DIR / 'access_token.json'
        
        logger.info("YandexMetrikaOAuth инициализирован")
    
    def get_authorization_url(self) -> str:
        """
        Получение URL для авторизации
        
        Returns:
            URL для перехода к авторизации
        """
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri
        }
        
        url = f"{OAUTH_AUTHORIZE_URL}?{urlencode(params)}"
        logger.info(f"Сгенерирован URL авторизации: {url}")
        return url
    
    def authorize(self, open_browser: bool = True) -> str:
        """
        Запуск процесса авторизации
        
        Args:
            open_browser: Открыть браузер автоматически
            
        Returns:
            URL для авторизации
        """
        auth_url = self.get_authorization_url()
        
        print("\n" + "="*60)
        print("ОАУТОРИЗАЦИЯ ЯНДЕКС.МЕТРИКА")
        print("="*60)
        print(f"\nПерейдите по ссылке для авторизации:")
        print(f"{auth_url}\n")
        print("После авторизации вы будете перенаправлены на:")
        print(f"{self.redirect_uri}?code=XXXXX")
        print("\nСкопируйте код из параметра 'code' из URL после перенаправления.")
        
        if open_browser:
            try:
                webbrowser.open(auth_url)
                print("\nБраузер открыт автоматически.")
            except Exception as e:
                logger.warning(f"Не удалось открыть браузер: {e}")
        
        return auth_url
    
    def get_access_token(self, authorization_code: str) -> Dict:
        """
        Получение access token по коду авторизации
        
        Args:
            authorization_code: Код авторизации из redirect URI
            
        Returns:
            Словарь с токеном и информацией
        """
        data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        try:
            response = requests.post(OAUTH_TOKEN_URL, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Сохраняем токен
            self.save_token(token_data)
            
            logger.info("Access token успешно получен")
            return token_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при получении токена: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Ответ сервера: {e.response.text}")
            raise
    
    def save_token(self, token_data: Dict) -> Path:
        """
        Сохранение токена в файл
        
        Args:
            token_data: Данные токена
            
        Returns:
            Путь к файлу с токеном
        """
        with open(self.token_file, 'w', encoding='utf-8') as f:
            json.dump(token_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Токен сохранен в {self.token_file}")
        return self.token_file
    
    def load_token(self) -> Optional[Dict]:
        """
        Загрузка токена из файла
        
        Returns:
            Данные токена или None
        """
        if not self.token_file.exists():
            return None
        
        try:
            with open(self.token_file, 'r', encoding='utf-8') as f:
                token_data = json.load(f)
            
            logger.info("Токен загружен из файла")
            return token_data
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке токена: {e}")
            return None
    
    def get_valid_token(self) -> Optional[str]:
        """
        Получение валидного access token
        
        Returns:
            Access token или None
        """
        token_data = self.load_token()
        
        if not token_data:
            return None
        
        access_token = token_data.get('access_token')
        
        # Проверяем, не истек ли токен
        # В реальном приложении нужно проверять expires_in и обновлять токен
        if access_token:
            return access_token
        
        return None
    
    def extract_code_from_url(self, url: str) -> Optional[str]:
        """
        Извлечение кода авторизации из redirect URL
        
        Args:
            url: URL с кодом авторизации
            
        Returns:
            Код авторизации или None
        """
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            code = params.get('code', [None])[0]
            return code
        except Exception as e:
            logger.error(f"Ошибка при извлечении кода: {e}")
            return None


def interactive_authorization():
    """
    Интерактивная авторизация через консоль
    """
    oauth = YandexMetrikaOAuth()
    
    # Запускаем авторизацию
    auth_url = oauth.authorize(open_browser=True)
    
    # Ждем ввода кода
    print("\n" + "-"*60)
    code = input("Введите код авторизации из URL (или полный URL с кодом): ").strip()
    
    # Если введен полный URL, извлекаем код
    if code.startswith('http'):
        code = oauth.extract_code_from_url(code)
    
    if not code:
        print("Ошибка: код авторизации не найден")
        return None
    
    try:
        # Получаем токен
        token_data = oauth.get_access_token(code)
        print("\n✓ Авторизация успешна!")
        print(f"Access token: {token_data.get('access_token', 'N/A')[:20]}...")
        print(f"Токен сохранен в: {oauth.token_file}")
        return token_data
        
    except Exception as e:
        print(f"\n✗ Ошибка авторизации: {e}")
        return None


if __name__ == '__main__':
    interactive_authorization()

