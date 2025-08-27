FROM python:3.10-slim-bullseye

WORKDIR /wb_price_check_bot

COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y \
    vim \
    wget \
    supervisor \
    --no-install-recommends

# Загрузка и установка Chrome
RUN wget https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_139.0.7258.154-1_amd64.deb \
    && dpkg -i google-chrome-stable_134.0.6998.35-1_amd64.deb \
    || apt-get install -f -y \
    && dpkg -i google-chrome-stable_134.0.6998.35-1_amd64.deb \
    && rm google-chrome-stable_134.0.6998.35-1_amd64.deb

# Загрузка и распаковка ChromeDriver
RUN wget https://storage.googleapis.com/chrome-for-testing-public/139.0.7258.154/linux64/chromedriver-linux64.zip
RUN unzip chromedriver-linux64.zip
RUN chmod +x /wb_price_check_bot/chromedriver-linux64/chromedriver

# Очистка кэша для уменьшения образа
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .
# Создаем файл конфигурации Supervisor
RUN echo "[supervisord]\n" > /etc/supervisor/conf.d/supervisord.conf
RUN echo "nodaemon=true\n" >> /etc/supervisor/conf.d/supervisord.conf

RUN echo "[program:main]\n" >> /etc/supervisor/conf.d/supervisord.conf
RUN echo "command=/usr/local/bin/python /wb_price_check_bot/src/main.py\n" >> /etc/supervisor/conf.d/supervisord.conf
RUN echo "autostart=true\n" >> /etc/supervisor/conf.d/supervisord.conf
RUN echo "autorestart=true\n" >> /etc/supervisor/conf.d/supervisord.conf
RUN echo "stderr_logfile=/dev/stderr\n" >> /etc/supervisor/conf.d/supervisord.conf
RUN echo "stdout_logfile=/dev/stdout\n" >> /etc/supervisor/conf.d/supervisord.conf

RUN echo "[program:consumer]\n" >> /etc/supervisor/conf.d/supervisord.conf
RUN echo "command=/usr/local/bin/python /wb_price_check_bot/rabbitmq/consumer.py\n" >> /etc/supervisor/conf.d/supervisord.conf
RUN echo "autostart=true\n" >> /etc/supervisor/conf.d/supervisord.conf
RUN echo "autorestart=true\n" >> /etc/supervisor/conf.d/supervisord.conf
RUN echo "stderr_logfile=/dev/stderr\n" >> /etc/supervisor/conf.d/supervisord.conf
RUN echo "stdout_logfile=/dev/stdout\n" >> /etc/supervisor/conf.d/supervisord.conf

# Запускаем Supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]