"""
Пакет config.

Содержит константы и настройки, необходимые для работы бота.

Экспортируемые переменные:
    TOKEN (str): Токен Telegram-бота.
    PROJECT_PATH (str): Путь к корневой директории проекта.
    DB_CONN (list): Данные для подключения к БД.
    DEST (int): ID пункта выдачи заказов.
    CURRENCY (str): Обозначение валюты, в которой отображена стоимость книги.
    RABBIT_LOGIN(str): Логин для брокера сообщений.
    RABBIT_PASSWORD(str): Пароль для брокера сообщений.
    CONFIG_FILE_PATH(str): Путь к файлу конфигурации.
    LOG_FILE_PATH(str): Путь к файлу сохранения общих логов.
    CONSUMER_LOG_FILE_PATH(str): Путь к файлу сохранения логов rabbitmq/consumer.py.
    PRODUCER_LOG_FILE_PATH(str): Путь к файлу сохранения логов rabbitmq/producer.py.
    PRICE_CHECKER_LOG_FILE_PATH(str): Путь к файлу сохранения логов parser/get_price.
"""

from config.constants import (
    TOKEN, 
    PROJECT_PATH,
    DB_CONN,
    DEST,
    CURRENCY,
    RABBIT_LOGIN,
    RABBIT_PASSWORD,
    CONFIG_FILE_PATH,
    LOG_FILE_PATH,
    CONSUMER_LOG_FILE_PATH,
    PRODUCER_LOG_FILE_PATH,
    PRICE_CHECKER_LOG_FILE_PATH,
)
