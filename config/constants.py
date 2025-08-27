"""
Модуль config.constants

Содержит константы и настройки, используемые в проекте, такие как токен бота,
данные подключения к PostgreSQL.
"""

import os
import sys
from utils import get_bot_token, get_db_connection_params, update_config_file


update_config_file()

# Абсолютный путь к корневой директории проекта.
# Используется os.path.dirname(__file__) для получения пути к текущему файлу (constants.py),
# затем переход на один уровень выше, для получения пути к PROJECT_PATH.
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Путь к проекту в sys.path, для возможности импортировать модули из проекта.
sys.path.insert(0, PROJECT_PATH)

# Получение токен бота из переменной окружения или файла конфигурации (см. utils.py).
TOKEN = get_bot_token()

# Получение данных подключения к базе данных из переменной окружения или файла конфигурации (см. utils.py).
DB_CONN = get_db_connection_params()

# Валюта, для получения стоимости
CURRENCY = 'rub'
# Код пункта выдачи заказа
DEST = '-1255942'

# Данные для входа в брокер сообщений
RABBIT_LOGIN = "guest"
RABBIT_PASSWORD = "guest"

CONFIG_FILE_PATH = os.path.join(PROJECT_PATH, "src", "config.yaml")

LOG_FILE_PATH = os.path.join(PROJECT_PATH, "logs", "bot.log")
CONSUMER_LOG_FILE_PATH = os.path.join(PROJECT_PATH, "logs", "consumer.log")
PRODUCER_LOG_FILE_PATH = os.path.join(PROJECT_PATH, "logs", "producer.log")
PRICE_CHECKER_LOG_FILE_PATH = os.path.join(PROJECT_PATH, "logs", "price_cheker.log")
