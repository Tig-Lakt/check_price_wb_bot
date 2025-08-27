
"""
Этот модуль инициализирует пакет, импортируя функции для получения данных конфигурации:

- `get_bot_token`: Функция для получения токена бота.
- `get_db_connection_params`: Функция для получения параметров подключения к базе данных.
- `update_config_file`: Функция для конфигурационного файла.
"""

from utils.get_data import (
    get_bot_token, 
    get_db_connection_params, 
    update_config_file,
)

from utils.logging_config import setup_logging