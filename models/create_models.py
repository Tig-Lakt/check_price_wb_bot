import logging
from database.database import DataBase


logger = logging.getLogger("wb_check_price_bot.handlers.users")


async def create_models():
    """
    Создает таблицу books в базе данных, если она еще не существуют и заполняет ее начальными
    данными.

    В случае ошибки при работе с базой данных, выводит сообщение об ошибке.
    """
    db = DataBase()
    if await db.connect():
        try:
            # Создание таблицу books
            await db.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    id BIGSERIAL,
                    book_id BIGINT PRIMARY KEY,
                    book_name TEXT NOT NULL,
                    price TEXT NOT NULL
                );''')
            # Заполнение таблицы подготовленными данными
            await db.execute('''
                INSERT INTO books(book_id, book_name, price) VALUES
                    (6034394, 'Чистый код', '0'),
                    (12989895, 'Чистый AGILE', '0'),
                    (6411515, 'Идеальный программист', '0'),
                    (5417786, 'Чистая архитектура', '0'),
                    (94341513, 'Идеальная работа', '0')
                    ON CONFLICT (book_id) DO NOTHING;
            ''')

        except Exception as e:
            logger.error(f"Ошибка при работе с базой данных: {e}")

        finally:
            await db.close()