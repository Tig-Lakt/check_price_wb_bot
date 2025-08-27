## Требования
Docker  
Docker Compose  
Python 3.8+ 

### Зависимости

*   **Фреймворк бота:** `aiogram~=3.0`
*   **Работа с БД:** `asyncpg~=0.30`
*   **Работа с RabbitMQ:** `aio-pika~=9.5`
*   **Загрузка конфигов:** `dotenv~=0.9`

### Установка и настройка
1. Клонирование репозитория

```bash
git clone https://github.com/Tig-Lakt/check_price_wb_bot/  
cd <project-directory>
```

2. Настройка переменных окружения  

Создайте файл .env в корневой директории проекта:

```bash
touch .env
```

### Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=telegram_bot_token  

### PostgreSQL Configuration
DB_NAME=database_name  
DB_USER=database_user  
DB_PASSWORD=database_password  
DB_HOST=postgres  
DB_PORT=5432  

### RabbitMQ Configuration
RABBIT_LOGIN=rabbitmq_user  
RABBIT_PASSWORD=rabbitmq_password  

3. Запуск приложения

```bash
# Запуск всех сервисов
docker-compose up -d
```
