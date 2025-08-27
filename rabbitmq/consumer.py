import asyncio
import json
import logging
import os
import sys

import aio_pika
from aio_pika.abc import AbstractIncomingMessage


PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_PATH)

from config import DB_CONN, RABBIT_LOGIN, RABBIT_PASSWORD, CONSUMER_LOG_FILE_PATH
from database.database import upd_book_data


def setup_consumer_logging() -> logging.Logger:
    """
    Настройка логирования для consumer.py.
    """
    
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    logger = logging.getLogger("wb_check_price_bot.rabbitmq.consumer")
    logger.setLevel(logging.INFO)
    
    # Очистка существующих обработчиков
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Файловый обработчик
    file_handler = logging.handlers.RotatingFileHandler(
        filename=CONSUMER_LOG_FILE_PATH,
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
    
    logger.info("Логирование consumer настроено")
    return logger


# Инициализация логгера
logger = setup_consumer_logging()


async def process_message(message: AbstractIncomingMessage) -> None:
    """
    Асинхронная функция для обработки входящих сообщений из очереди RabbitMQ.
    """
    async with message.process():
        body = message.body.decode()
        try:
            message_data = json.loads(body)
            # Обновление данных книги в базе данных
            await upd_book_data(
                str(message_data["price"]), 
                int(message_data["book_id"])
            )
            logger.info(
                "Обработано сообщение: book_id=%s, price=%s",
                message_data["book_id"], message_data["price"]
            )
                  
        except json.JSONDecodeError:
            logger.error("Ошибка декодирования JSON: %s", body)
        except KeyError as e:
            logger.error("Отсутствует обязательное поле %s в сообщении: %s", e, body)
        except ValueError as e:
            logger.error("Ошибка преобразования данных: %s, body: %s", e, body)
        except Exception as e:
            logger.error("Неожиданная ошибка при обработке сообщения: %s, body: %s", e, body)


async def main() -> None:
    """
    Основная асинхронная функция.
    """
    logger.info("Запуск RabbitMQ consumer...")
    
    connection_string = f"amqp://{RABBIT_LOGIN}:{RABBIT_PASSWORD}@{DB_CONN[0]}/"
    
    try:
        connection = await aio_pika.connect_robust(connection_string)
        logger.info("Подключение к RabbitMQ установлено")
        
        async with connection:
            channel = await connection.channel()
            logger.debug("Канал RabbitMQ создан")
            
            # Создание очереди
            queue = await channel.declare_queue("my_queue",)
            logger.info("Очередь 'my_queue' объявлена")
            
            await queue.consume(process_message)
            logger.info("Подписка на очередь оформлена")
            
            logger.info("Ожидаю сообщения из очереди 'my_queue'...")
            print("Consumer запущен. Ожидаю сообщения...")
            
            await asyncio.Future()
            
    except ConnectionError as e:
        logger.critical("Ошибка подключения к RabbitMQ: %s", e)
        raise
    except Exception as e:
        logger.critical("Неожиданная ошибка: %s", e, exc_info=True)
        raise


if __name__ == "__main__":
    """
    Точка входа для consumer.
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Завершение работы по запросу пользователя")
    except Exception as e:
        logger.critical("Критическая ошибка: %s", e, exc_info=True)
        sys.exit(1)