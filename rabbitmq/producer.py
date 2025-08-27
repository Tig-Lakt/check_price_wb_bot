import json
import logging
import os
import sys
from typing import Dict, Any

import aio_pika
from aio_pika import Message
from aio_pika.abc import AbstractRobustConnection


PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_PATH)


from config import DB_CONN, RABBIT_LOGIN, RABBIT_PASSWORD, PRODUCER_LOG_FILE_PATH


def setup_producer_logging() -> logging.Logger:
    """
    Настройка логирования для RabbitMQ producer.
    """
     
    # Форматтер
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Создание логгера
    logger = logging.getLogger("wb_check_price_bot.rabbitmq.producer")
    logger.setLevel(logging.INFO)
    
    # Очистка существующих обработчиков
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Файловый обработчик
    file_handler = logging.handlers.RotatingFileHandler(
        filename=PRODUCER_LOG_FILE_PATH,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Добавление обработчиков
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info("Логирование producer настроено")
    return logger


# Инициализация логгера
logger = setup_producer_logging()


async def send_message(message_data: Dict[str, Any]) -> None:
    """
    Асинхронная функция для отправки сообщения в очередь RabbitMQ.
    
    Args:
        message_data: Словарь с данными для отправки
    """
    try:
        # Формирование строки подключения к RabbitMQ
        connection_url = f"amqp://{RABBIT_LOGIN}:{RABBIT_PASSWORD}@{DB_CONN[0]}/"
        
        logger.debug("Подключение к RabbitMQ: %s", connection_url)
        
        # Использование context manager для автоматического управления соединением
        connection: AbstractRobustConnection = await aio_pika.connect_robust(connection_url)
        
        async with connection:
            channel = await connection.channel()
            logger.debug("Канал RabbitMQ создан")
            
            # Объявление очереди
            queue = await channel.declare_queue(
                "my_queue",
            )
            logger.debug("Очередь 'my_queue' объявлена")
            
            # Преобразование данных в JSON
            message_text = json.dumps(message_data)
            
            # Создание сообщения
            message = Message(
                body=message_text.encode(),
            )
            logger.debug("Сообщение создано")
            
            # Публикация сообщение в очередь
            await channel.default_exchange.publish(
                message, 
                routing_key=queue.name
            )
            
            logger.info(
                "Отправлено сообщение: book_id=%s, price=%s",
                message_data.get("book_id"), message_data.get("price")
            )
            
    except ConnectionError as e:
        logger.error("Ошибка подключения к RabbitMQ: %s", e, exc_info=True)
        raise
        
    except Exception as e:
        logger.error(
            "Ошибка при отправке сообщения %s: %s",
            message_data, e,
            exc_info=True
        )
        raise