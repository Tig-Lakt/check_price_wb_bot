import asyncio
import json
import logging
import os
import sys
import time
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_PATH)


from config import CURRENCY, DEST, PRICE_CHECKER_LOG_FILE_PATH
from database.database import get_book_data
from rabbitmq import send_message


def setup_price_checker_logging() -> logging.Logger:
    """
    Настройка логирования для скрипта проверки цен.
    """
    
    # Форматтер
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Создание логгера
    logger = logging.getLogger("wb_check_price_bot.price_checker")
    logger.setLevel(logging.INFO)
    
    # Очистка существующих обработчиков
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Файловый обработчик
    file_handler = logging.handlers.RotatingFileHandler(
        filename=PRICE_CHECKER_LOG_FILE_PATH,
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
    
    logger.info("Логирование price_checker настроено")
    return logger


# Инициализация логгера
logger = setup_price_checker_logging()


def get_price_with_selenium(vendor_code: str) -> Optional[float]:
    """
    Синхронная функция для получения цены через Selenium.
    
    Args:
        vendor_code (str): Артикул книги.
        
    Returns:
        Optional[float]: Цена товара или None в случае ошибки.
    """
    driver = create_driver()
    
    try:
        logger.debug("Запуск Selenium для артикула: %s", vendor_code)
        
        url = (
            f"https://card.wb.ru/cards/v4/detail?appType=1&curr={CURRENCY}"
            f"&dest={DEST}&spp=30&ab_testing=false&lang=ru&nm={vendor_code}"
        )
        
        logger.debug("Открытие URL: %s", url)
        driver.get(url)
        time.sleep(5)  # Ожидание загрузки страницы
        
        # Получение данных из элемента pre
        data_element = driver.find_element(By.TAG_NAME, "pre")
        json_data = json.loads(data_element.text)
        
        # Извлечение цены
        product_info = json_data["products"][0]
        price_info = product_info["sizes"][0]["price"]
        
        # Вычисление итоговой цены
        price = (price_info["product"] + price_info["logistics"]) / 100
        logger.info("Получена цена для артикула %s: %s", vendor_code, price)
        
        return price
        
    except Exception as e:
        logger.error(
            "Ошибка при получении цены для артикула %s: %s",
            vendor_code, e,
            exc_info=True
        )
        return None
        
    finally:
        driver.close()
        driver.quit()
        logger.debug("Драйвер Selenium закрыт для артикула %s", vendor_code)


def create_driver() -> webdriver.Chrome:
    """
    Создает и настраивает экземпляр веб-драйвера Chrome для Selenium.
    """
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=chrome_options)
        logger.debug("Создан новый Chrome driver")
        return driver
        
    except Exception as e:
        logger.critical("Ошибка создания Chrome driver: %s", e, exc_info=True)
        raise


async def process_single_book(book_data: dict) -> None:
    """
    Асинхронно обрабатывает один товар: получает цену и отправляет в RabbitMQ.
    """
    vendor_code = book_data["book_id"]
    book_name = book_data.get("book_name", "Unknown")
    
    try:
        logger.info("Обработка книги: %s (%s)", book_name, vendor_code)
        
        # Запуск Selenium в отдельном потоке
        loop = asyncio.get_event_loop()
        price = await loop.run_in_executor(
            None, get_price_with_selenium, vendor_code
        )
        
        # Формирование данных для отправки
        price_display = "Нет в наличии" if price is None else price
        data = {
            "book_id": vendor_code,
            "price": price_display
        }
        
        # Асинхронная отправка сообщение в RabbitMQ
        await send_message(data)
        logger.info("Сообщение отправлено в RabbitMQ для артикула %s", vendor_code)
        
    except Exception as e:
        logger.error(
            "Ошибка при обработке артикула %s: %s",
            vendor_code, e,
            exc_info=True
        )


async def get_books_id() -> None:
    """
    Основная асинхронная функция: получает данные из БД и обрабатывает книги.
    """
    try:
        logger.info("Запуск процесса проверки цен")
        start_time = time.time()
        
        # Асинхронное получение данных из БД
        books_data = await get_book_data()
        
        if not books_data:
            logger.warning("Не удалось получить данные из базы данных")
            return
        
        logger.info("Найдено %d книг для обработки", len(books_data))
        
        # Создание задачи для параллельной обработки
        tasks = [
            process_single_book(book_data) 
            for book_data in books_data
        ]
        
        await asyncio.gather(*tasks)
        
        end_time = time.time()
        logger.info(
            "Обработка завершена за %.2f секунд",
            end_time - start_time
        )
        
    except Exception as e:
        logger.critical(
            "Критическая ошибка в основном процессе: %s",
            e,
            exc_info=True
        )
        raise


if __name__ == "__main__":
    try:
        start_time = time.time()
        logger.info("Запуск скрипта проверки цен. Время начала: %s", time.time())
        
        asyncio.run(get_books_id())
        
        end_time = time.time()
        logger.info(
            "Скрипт завершен. Общее время выполнения: %.2f секунд",
            end_time - start_time
        )
        
    except KeyboardInterrupt:
        logger.info("Завершение работы по запросу пользователя")
        
    except Exception as e:
        logger.critical(
            "Непредвиденная ошибка при запуске скрипта: %s",
            e,
            exc_info=True
        )
        sys.exit(1)