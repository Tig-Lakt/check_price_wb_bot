import os
import sys
import asyncio


project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_path)

# Настройка логирования
from utils.logging_config import setup_logging
logger = setup_logging("INFO")

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

from config import TOKEN
from handlers import commands_handler, users_handler
from models import create_models


async def main():
    """
    Инициализирует и запускает Telegram-бота.
    """
    logger.info("Запуск инициализации бота...")
    
    try:
        bot = Bot(
            token=TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        dp = Dispatcher()

        # Регистрация роутеров
        dp.include_routers(
            commands_handler.router,
            users_handler.router,
        )

        # Создаются таблицы в БД
        await create_models()
        logger.debug("Модели базы данных созданы")
        
        # Очистка вебхуков
        await bot.delete_webhook(drop_pending_updates=True)
        logger.debug("Вебхук очищен")
        
        # Запуск бота
        logger.info("Запуск polling...")
        try:
            await dp.start_polling(bot)
        finally:
            logger.info("Бот завершил работу")
        
    except Exception as e:
        logger.critical(f"Ошибка при запуске бота: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)