import logging
import logging.handlers
import os


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Настройка логирования для всего проекта.
    
    Args:
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        logging.Logger: Настроенный логгер
    """
    PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    LOG_FILE_PATH = os.path.join(PROJECT_PATH, "logs", "bot.log")

    log_dir = os.path.dirname(LOG_FILE_PATH)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Форматтер для всех логов
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Уровень логирования
    level = getattr(logging, log_level.upper())
    
    # Основной логгер проекта
    logger = logging.getLogger("wb_check_price_bot")
    logger.setLevel(level)
    
    # Очистка существующих обработчиков
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Файловый обработчик (ротация по размеру)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=LOG_FILE_PATH,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    
    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Добавление обработчиков
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
       
    logger.info("Логирование настроено с уровнем %s", log_level)
    return logger  