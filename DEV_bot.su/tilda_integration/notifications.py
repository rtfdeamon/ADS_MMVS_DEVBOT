"""
Модуль для отправки уведомлений о новых заявках из форм Tilda
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
import requests

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, EMAIL_NOTIFICATIONS

logger = logging.getLogger(__name__)


class NotificationService:
    """Сервис для отправки уведомлений"""
    
    def __init__(self):
        self.telegram_token = TELEGRAM_BOT_TOKEN
        self.telegram_chat_id = TELEGRAM_CHAT_ID
        self.email_to = EMAIL_NOTIFICATIONS
        
        logger.info("NotificationService инициализирован")
    
    def send_telegram_notification(self, form_data: Dict) -> bool:
        """
        Отправка уведомления в Telegram
        
        Args:
            form_data: Данные формы
            
        Returns:
            True если уведомление отправлено успешно
        """
        if not self.telegram_token or not self.telegram_chat_id:
            logger.warning("Telegram токен или chat_id не настроены")
            return False
        
        # Формирование сообщения
        fields = form_data.get('fields', {})
        message = f"🔔 *Новая заявка с сайта*\n\n"
        message += f"*Форма:* {form_data.get('form_name', 'N/A')}\n"
        message += f"*Страница:* {form_data.get('page_url', 'N/A')}\n\n"
        
        for field_name, field_value in fields.items():
            message += f"*{field_name}:* {field_value}\n"
        
        message += f"\n_Время:_ {form_data.get('timestamp', 'N/A')}"
        
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        
        payload = {
            'chat_id': self.telegram_chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info("Уведомление в Telegram отправлено")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при отправке в Telegram: {e}")
            return False
    
    def send_email_notification(self, form_data: Dict) -> bool:
        """
        Отправка уведомления на email
        
        Args:
            form_data: Данные формы
            
        Returns:
            True если email отправлен успешно
        """
        if not self.email_to:
            logger.warning("Email для уведомлений не настроен")
            return False
        
        # Формирование письма
        fields = form_data.get('fields', {})
        
        subject = f"Новая заявка: {form_data.get('form_name', 'Форма')}"
        
        body = f"""
Новая заявка с сайта dev-bot.su

Форма: {form_data.get('form_name', 'N/A')}
Страница: {form_data.get('page_url', 'N/A')}
Время: {form_data.get('timestamp', 'N/A')}

Данные формы:
"""
        for field_name, field_value in fields.items():
            body += f"{field_name}: {field_value}\n"
        
        try:
            # Простая отправка через SMTP (нужно настроить SMTP сервер)
            # Для продакшена лучше использовать SendGrid, Mailgun и т.д.
            msg = MIMEMultipart()
            msg['From'] = 'noreply@dev-bot.su'
            msg['To'] = self.email_to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Здесь нужно настроить SMTP сервер
            # smtp_server = smtplib.SMTP('smtp.example.com', 587)
            # smtp_server.starttls()
            # smtp_server.login('user', 'password')
            # smtp_server.send_message(msg)
            # smtp_server.quit()
            
            logger.info(f"Email уведомление подготовлено для {self.email_to}")
            logger.warning("SMTP сервер не настроен, email не отправлен")
            return False
            
        except Exception as e:
            logger.error(f"Ошибка при отправке email: {e}")
            return False
    
    def send_notification(self, form_data: Dict, channels: list = None) -> Dict[str, bool]:
        """
        Отправка уведомлений по всем каналам
        
        Args:
            form_data: Данные формы
            channels: Список каналов ['telegram', 'email'] или None для всех
            
        Returns:
            Словарь с результатами отправки по каналам
        """
        if channels is None:
            channels = ['telegram', 'email']
        
        results = {}
        
        if 'telegram' in channels:
            results['telegram'] = self.send_telegram_notification(form_data)
        
        if 'email' in channels:
            results['email'] = self.send_email_notification(form_data)
        
        return results

