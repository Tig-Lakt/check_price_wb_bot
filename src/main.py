import asyncio

from init_bot import main


if __name__ == "__main__":
    """
    Точка входа в приложение.

    Запускает асинхронную функцию `main` из модуля `init_bot` с использованием `asyncio.run`.
    """
    asyncio.run(main())
