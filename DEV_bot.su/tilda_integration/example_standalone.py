#!/usr/bin/env python3
"""
Пример использования модуля интеграции с Tilda без Flask
Можно использовать для тестирования или как standalone скрипт
"""
import json
from webhook_handler import TildaWebhookHandler
from metrika_integration import MetrikaIntegration
from notifications import NotificationService


def example_process_form():
    """Пример обработки данных формы"""
    
    # Инициализация обработчиков
    webhook_handler = TildaWebhookHandler()
    metrika = MetrikaIntegration()
    notifications = NotificationService()
    
    # Пример данных формы (как приходят от Tilda)
    form_data_example = {
        'formid': '1023590156',
        'formname': 'Консультация',
        'pageid': '12345',
        'pageurl': 'https://dev-bot.su/',
        'fields': [
            {'name': 'name', 'value': 'Иван Иванов'},
            {'name': 'email', 'value': 'ivan@example.com'},
            {'name': 'phone', 'value': '+79001234567'},
            {'name': 'task', 'value': 'Нужна автоматизация продаж'}
        ]
    }
    
    print("Обработка данных формы...")
    
    # Обработка webhook
    result = webhook_handler.process_webhook(form_data_example)
    
    if result['success']:
        print(f"✅ Заявка обработана успешно!")
        print(f"   Форма ID: {result['form_id']}")
        print(f"   Сохранено в: {result['saved_to']}")
        
        # Отправка события в Metrika
        metrika.send_conversion_event(result['data'])
        print("✅ Событие отправлено в Yandex.Metrika")
        
        # Отправка уведомлений
        notification_results = notifications.send_notification(result['data'])
        print(f"✅ Уведомления отправлены: {notification_results}")
        
    else:
        print(f"❌ Ошибка: {result.get('error')}")


def example_get_statistics():
    """Пример получения статистики"""
    
    handler = TildaWebhookHandler()
    stats = handler.get_form_statistics(days=30)
    
    print("\n📊 Статистика по формам (последние 30 дней):")
    print(f"   Всего заявок: {stats['total_submissions']}")
    print(f"\n   По формам:")
    for form_id, count in stats['by_form_id'].items():
        print(f"     - {form_id}: {count} заявок")
    
    print(f"\n   По датам (топ 5):")
    sorted_dates = sorted(stats['by_date'].items(), key=lambda x: x[1], reverse=True)[:5]
    for date, count in sorted_dates:
        print(f"     - {date}: {count} заявок")


def example_get_metrika_code():
    """Пример получения кода для Metrika"""
    
    metrika = MetrikaIntegration()
    code = metrika.generate_metrika_code(goal_id='123456')
    
    print("\n📝 JavaScript код для вставки в Tilda:")
    print("=" * 60)
    print(code)
    print("=" * 60)
    print("\nИнструкция:")
    print("1. Скопируйте код выше")
    print("2. В Tilda откройте настройки формы")
    print("3. Перейдите в 'HTML код после отправки формы'")
    print("4. Вставьте код и сохраните")


if __name__ == '__main__':
    print("=" * 60)
    print("ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ ИНТЕГРАЦИИ С TILDA")
    print("=" * 60)
    
    # Пример 1: Обработка формы
    example_process_form()
    
    # Пример 2: Статистика
    example_get_statistics()
    
    # Пример 3: Код для Metrika
    example_get_metrika_code()
    
    print("\n" + "=" * 60)
    print("✅ Примеры выполнены!")
    print("=" * 60)

