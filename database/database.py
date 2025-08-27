
"""
Модуль database.py

Обеспечивает асинхронное взаимодействие с базой данных PostgreSQL
с использованием библиотеки asyncpg.  Параметры подключения загружаются
из переменных окружения.
"""

import asyncpg
import logging

# Настройка логирования
logger = logging.getLogger("wb_check_price_bot.database.database")

from config import DB_CONN


class DataBase:
    """
    Класс для управления подключением к базе данных PostgreSQL и выполнения запросов.
    Параметры подключения загружаются из переменных окружения.
    """
    def __init__(self):
        """
        Инициализирует объект DataBase с параметрами подключения из переменных окружения.

        Переменные окружения:
            DB_HOST (str): Хост базы данных.
            DB_PORT (str): Порт базы данных.
            DB_NAME (str): Имя базы данных.
            DB_USER (str): Имя пользователя базы данных.
            DB_PASSWORD (str): Пароль пользователя базы данных.

        Raises:
            ValueError: Если какая-либо из необходимых переменных окружения не установлена.
        """
        self.host = DB_CONN[0]
        self.port = DB_CONN[1]
        self.database = DB_CONN[2]
        self.user = DB_CONN[3]
        self.password = DB_CONN[4]

        if not all([self.host, self.port, self.database, self.user, self.password]):
            raise ValueError(
                "Необходимо установить переменные окружения: DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD"
            )

        self.connection = None
        self.dsn = (
            f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        )

    async def connect(self) -> bool:
        """
        Устанавливает асинхронное подключение к базе данных.

        Returns:
            bool: True, если подключение успешно установлено, False - в противном случае.
        """
        try:
            self.connection = await asyncpg.connect(self.dsn)
            logger.info("Успешно подключено к PostgreSQL!")
            return True
        except asyncpg.PostgresConnectionError as e:
            logger.error(f"Ошибка подключения к PostgreSQL: {e}")
            return False

    async def execute(self, query: str, *args) -> bool:
        """
        Выполняет асинхронный запрос к базе данных без возврата данных.

        Используется для выполнения операций INSERT, UPDATE, DELETE и CREATE.

        Args:
            query (str): SQL-запрос для выполнения.
            *args: Аргументы для подстановки в запрос.

        Returns:
            bool: True, если запрос успешно выполнен, False - в противном случае.
        """
        if self.connection is None:
            logger.error("Ошибка: Нет активного подключения к базе данных.")
            return False

        try:
            await self.connection.execute(query, *args)
            return True
        except Exception as e:
            logger.exception(f"Ошибка выполнения запроса: {e}") 
            return False

    async def fetch(self, query: str, *args) -> list[asyncpg.Record] | None:
        """
        Выполняет асинхронный запрос SELECT и возвращает результаты в виде списка.

        Args:
            query (str): SQL-запрос для выполнения.
            *args: Аргументы для подстановки в запрос.

        Returns:
            list[asyncpg.Record] | None: Список строк (asyncpg.Record),
            если запрос успешно выполнен, None - в случае ошибки или отсутствия подключения.
        """
        if self.connection is None:
            logger.error("Ошибка: Нет активного подключения к базе данных.")
            return None

        try:
            rows = await self.connection.fetch(query, *args)
            return rows
        except Exception as e:
            logger.exception(f"Ошибка выполнения запроса: {e}") 
            return None

    async def fetchrow(self, query: str, *args) -> asyncpg.Record | None:
        """
        Выполняет асинхронный запрос SELECT и возвращает одну строку.

        Args:
            query (str): SQL-запрос для выполнения.
            *args: Аргументы для подстановки в запрос.

        Returns:
            asyncpg.Record | None: Объект asyncpg.Record, представляющий строку,
            если запрос успешно выполнен, None - в случае ошибки или отсутствия подключения.
        """
        if self.connection is None:
            logger.error("Ошибка: Нет активного подключения к базе данных.")
            return None

        try:
            row = await self.connection.fetchrow(query, *args)
            return row
        except Exception as e:
            logger.exception(f"Ошибка выполнения запроса: {e}")
            return None

    async def close(self):
        """
        Закрывает асинхронное соединение с базой данных.
        """
        if self.connection:
            await self.connection.close()
            logger.info("Соединение с PostgreSQL закрыто.")
        else:
            logger.warning("Нет активного соединения для закрытия.")


async def upd_book_data(price: int, book_id: str, ):
    """
    Обновляет цену книги в базе данных.

    Args:
        book_name (str): Название книги.
        price (int): Стоимость книги.
    """
    db = DataBase()
    try:
        if not await db.connect():
            logger.error("Не удалось подключиться к базе данных.")
            return

        await db.execute(
            """UPDATE books
             SET price = $1
             WHERE book_id = $2;""",
            price,
            book_id,
        )

        logger.info(
            "Стоимость книги %s успешно обновлена, новая стоимость: %s",
            book_id, price
        )

    except Exception as e:
        logger.exception(f"Ошибка при работе с базой данных: {e}")
    finally:
        if db.connection:
            await db.close()


async def get_book_data() -> list[asyncpg.Record] | None:
    """
    Возвращает список всех book_id и book_name из базы данных.

    Returns:
        list[asyncpg.Record] | None: Список всех book_id и book_name,
        либо None в случае ошибки подключения или запроса.
    """
    db = DataBase()
    try:
        if not await db.connect():
            logger.error("Не удалось подключиться к базе данных.")
            return None

        books_id = await db.fetch("SELECT book_id, book_name FROM books;")
        logger.info(
            "Запрос get_book_data успешно обработан"
        )
        return books_id

    except Exception as e:
        logger.exception(f"Ошибка при работе с базой данных: {e}")
        return None
    finally:
        if db.connection:
            await db.close()
            
            
async def get_book_price(book_id) -> list[asyncpg.Record] | None:
    """
    Возвращает стоимость и название книги по book_id из базы данных.

    Returns:
        str[asyncpg.Record] | None: Стоимость и название книги по book_id,
        либо None в случае ошибки подключения или запроса.
    """
    db = DataBase()
    try:
        if not await db.connect():
            logger.error("Не удалось подключиться к базе данных.")
            return None

        books_price = await db.fetch(
            """SELECT book_name, price
                    FROM books
                    WHERE book_id = $1;""",
                    book_id
        )
        logger.info(
            "Запрос на получение стоимости для книги %s успешно обработан",
            book_id
        )
        
        return books_price

    except Exception as e:
        logger.exception(f"Ошибка при работе с базой данных: {e}")
        return None
    finally:
        if db.connection:
            await db.close()
            logger.info(
            "Соединение с БД закрыто"
        )