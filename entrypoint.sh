#!/bin/bash

# Инициализация цветовых констант
GREEN=$(TERM=xterm-256color tput setaf 2)
YELLOW=$(TERM=xterm-256color tput setaf 3)
RED=$(TERM=xterm-256color tput setaf 1)
RESET=$(TERM=xterm-256color tput sgr0)

cd /app

load_env() {
    if [ -f .env ]; then
        echo "Loading environment variables from .env file..."
        set -a
        source .env
        set +a
    fi
}

download_vendors() {
    echo "Downloading vendor files..."

    # Нормализация файла .vendors
    echo "Normalizing .vendors file..."
    dos2unix .vendors 2>/dev/null || true

    # Чтение и обработка файла
    while IFS='|' read -r path url; do
        # Очистка от пробелов и невидимых символов
        path=$(echo "$path" | tr -d '\r' | xargs)
        url=$(echo "$url" | tr -d '\r' | xargs)

        if [[ $path != \#* ]] && [[ -n "$path" ]] && [[ -n "$url" ]]; then
            echo "-----------------------------------"
            echo "Path: '$path'"
            echo "URL:  '$url'"
            echo "Target: '/app/static/vendor/$path'"

            mkdir -p "/app/static/vendor/$(dirname "$path")"
            if curl -L -f --retry 3 --retry-delay 2 "$url" -o "/app/static/vendor/$path"; then
                echo "${GREEN}Successfully downloaded $path${RESET}"
            else
                echo "${RED}ERROR: Failed to download $path${RESET}"
            fi
        fi
    done < <(grep -v '^\s*#\|^\s*$' .vendors)

    echo "-----------------------------------"
    echo "${GREEN}Finished downloading vendor files${RESET}"
    echo "Vendor directory contents:"
    ls -R /app/static/vendor/
}

setup_django() {
    echo 'Collecting static files...'

    echo "Checking staticfiles directory..."
    ls -la /app/staticfiles

    echo "Checking source static directory..."
    ls -la /app/static

    echo "Running collectstatic..."
    python manage.py collectstatic --noinput --clear -v 2

    # Проверка успешности сбора статических файлов
    if [ $? -ne 0 ]; then
        echo "${RED}ERROR: Failed to collect static files${RESET}"
        return 1
    fi

    # Установка права доступа к статическим файлам
    echo "Setting permissions for static files..."
    chown -R www-data:www-data /app/staticfiles
    chmod -R 555 /app/staticfiles  # r-xr-xr-x - только для чтения для всех

    echo "${GREEN}Static files collected successfully${RESET}"
    echo "Contents of staticfiles directory:"
    ls -la /app/staticfiles

    # Проверка прав доступа
    echo "Checking permissions..."
    stat /app/staticfiles
    stat /app/static

    echo "Checking Apache configuration..."
    apache2ctl -t

    echo 'Running migrations...'
    python manage.py migrate

    echo 'Initializing database...'
    if ! python manage.py setdb --force; then
        echo "${RED}ERROR: Failed to initialize database${RESET}"
        return 1
    fi
    echo "${GREEN}Database initialized successfully${RESET}"
}

run_server() {
    # Настройка и запуск Apache
    echo 'Configuring and starting Apache...'

    # Инициализация необходимых модулей Apache
    a2enmod proxy
    a2enmod proxy_http
    a2enmod headers
    a2enmod alias
    a2enmod expires
    a2enmod mime

    # Копирование конфигурации и запуск Apache
    cp /app/ska/management/release/apache.conf /etc/apache2/sites-available/000-default.conf
    rm -f /var/run/apache2/apache2.pid
    service apache2 start

    # Проверка статуса Apache
    if ! service apache2 status > /dev/null; then
        echo "${RED}ERROR: Apache failed to start${RESET}"
        echo "Apache error log:"
        tail -n 50 /var/log/apache2/error.log
        return 1
    fi

    echo "${GREEN}Apache started successfully${RESET}"

    if grep -q 'DJANGO_DEBUG=True' .env; then
        echo 'Starting development server...'
        python manage.py runserver 0.0.0.0:8000
    else
        python manage.py runrelease
    fi
}

start() {
    load_env
    download_vendors
    setup_django
    run_server
}

monitor_env() {
    echo "Starting .env file monitoring..."
    (
        while true; do
            if [ ! -f .env ]; then
                echo "Waiting for .env file to be created..."
                inotifywait -e create,moved_to -q /app
                if [ -f .env ]; then
                    echo "${YELLOW}WARNING: .env file was created${RESET}"
                    echo "${YELLOW}Please restart container to apply changes${RESET}"
                fi
            else
                echo "Watching .env file for changes..."
                inotifywait -e modify,delete,move,close_write -q /app/.env
                if [ -f .env ]; then
                    echo "${YELLOW}WARNING: .env file was modified${RESET}"
                    echo "${YELLOW}Please restart container to apply changes${RESET}"
                else
                    echo "${YELLOW}WARNING: .env file was deleted${RESET}"
                fi
            fi
        done
    ) &
}

# Первоначальная настройка и запуск
if [ -f .env ]; then
    start
else
    echo "${YELLOW}WARNING: .env file does not exist${RESET}"
    echo "${YELLOW}Please create it by using the 'python manage.py setenv' command${RESET}"
fi

# Запуск мониторинга в фоне
monitor_env &
exec tail -f /dev/null