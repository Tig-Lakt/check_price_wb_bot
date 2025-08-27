import logging
import os
import sys
from typing import List, Optional, Dict, Any

import yaml
from dotenv import load_dotenv

# Добавление корневого каталога проекта в PYTHONPATH для удобства импорта
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_PATH)

# Загрузка переменных окружения из файла .env
dotenv_path = os.path.join(PROJECT_PATH, ".env")
load_dotenv(dotenv_path, override=True)

CONFIG_FILE_PATH = os.path.join(PROJECT_PATH, "src", "config.yaml")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_bot_token() -> Optional[str]:
    """
    Получает токен бота из переменной окружения TELEGRAM_BOT_TOKEN.

    Returns:
        Optional[str]: Токен бота или None, если не задан.
    
    Raises:
        EnvironmentError: Если токен не задан (закомментировано)
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("Переменная окружения TELEGRAM_BOT_TOKEN не задана.")
        return None

    return token


def update_config_file(
    token: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    database: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
) -> None:
    """
    Обновляет config.yaml с токеном бота и/или параметрами базы данных.

    Args:
        token: Токен бота.
        host: Хост базы данных.
        port: Порт базы данных.
        database: Имя базы данных.
        user: Имя пользователя базы данных.
        password: Пароль базы данных.
    """
    config_data: Dict[str, Any] = {}
    
    # Добавление токена бота, если передан
    if token is not None:
        config_data["bot_token"] = token
        logger.info("Токен бота добавлен в конфигурацию")

    # Добавление параметров БД, если передан хост
    if host is not None:
        config_data.update({
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password
        })
        logger.info("Параметры базы данных добавлены в конфигурацию")

    # Если не передано никаких данных для обновления
    if not config_data:
        logger.warning("Не передано данных для обновления конфигурации")
        return

    try:
        # Чтение существующей конфигурации, если файл есть
        existing_config = {}
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as file:
                existing_config = yaml.safe_load(file) or {}
        
        # Обновление только переданных полей
        existing_config.update(config_data)
        
        # Запись обновленной конфигурации
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as file:
            yaml.dump(existing_config, file, default_flow_style=False)
            
        logger.info(f"Конфигурационный файл успешно обновлен: {CONFIG_FILE_PATH}")
        
    except IOError as e:
        logger.error(f"Ошибка ввода-вывода при работе с config.yaml: {e}")
    except yaml.YAMLError as e:
        logger.error(f"Ошибка YAML при записи config.yaml: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при обновлении config.yaml: {e}")


def get_db_connection_params() -> List[Optional[str]]:
    """
    Извлекает параметры подключения к базе данных из файла конфигурации.

    Приоритет: переменные окружения > конфигурационный файл

    Returns:
        List[Optional[str]]: Параметры подключения [host, port, database, user, password].
    """
    try:
        # Загрузка конфигурации из файла
        config = {}
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file) or {}
        
        # Получение параметров с приоритетом переменных окружения
        connection_params = [
            os.environ.get("DB_HOST") or config.get("host"),
            os.environ.get("DB_PORT") or config.get("port"),
            os.environ.get("DB_NAME") or config.get("database"),
            os.environ.get("DB_USER") or config.get("user"),
            os.environ.get("DB_PASSWORD") or config.get("password"),
        ]
        
        # Проверка, что все обязательные параметры есть
        if not all(connection_params):
            missing_params = [
                param_name for param_name, param_value in zip(
                    ["host", "port", "database", "user", "password"], 
                    connection_params
                ) if not param_value
            ]
            logger.warning(f"Отсутствуют параметры подключения: {missing_params}")
        
        return connection_params
        
    except FileNotFoundError:
        logger.error(f"Файл конфигурации не найден: {CONFIG_FILE_PATH}")
        return [None, None, None, None, None]
    except yaml.YAMLError as e:
        logger.error(f"Ошибка YAML при чтении файла конфигурации: {e}")
        return [None, None, None, None, None]
    except Exception as e:
        logger.error(f"Неожиданная ошибка при чтении конфигурации: {e}")
        return [None, None, None, None, None]