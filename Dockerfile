# Использование официального образа Python 3.12 slim для минимального размера
FROM python:3.12-slim

# Установка базовых пакетов
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        dos2unix=7.4.3-1 \
        ca-certificates=20230311 \
        gnupg=2.2.40-1.1 \
    && apt-mark hold dos2unix ca-certificates gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование файлов конфигурации
COPY .requirements .vendors ./

# Нормализация конфигурационных файлов
RUN dos2unix .requirements .vendors

# Установка системных зависимостей
RUN set -e \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
    # Установка остальных системных пакетов
    && remaining_packages=$(sed -n '/^\[system\]/,/^\[/p' .requirements | \
       grep "==" | grep -v "^ca-certificates\|^gnupg" | \
       grep -v "^\[" | cut -d= -f1) \
    && for pkg in $remaining_packages; do \
           echo "Installing $pkg..." \
           && apt-get install -y --no-install-recommends "$pkg" || exit 1; \
       done \
    # Фиксация версий пакетов
    && sed -n '/^\[system\]/,/^\[/p' .requirements | grep "==" | \
       grep -v "^\[" | cut -d= -f1 | xargs apt-mark hold \
    # Включение необходимых модулей Apache
    && a2enmod proxy \
    && a2enmod proxy_http \
    && a2enmod proxy_balancer \
    && a2enmod lbmethod_byrequests \
    && a2enmod headers \
    && a2enmod expires \
    && a2enmod alias \
    && a2enmod mime \
    # Очистка кэша apt для уменьшения размера образа
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    # Настройка директорий Apache
    && mkdir -p /var/log/apache2 \
    && mkdir -p /var/run/apache2 \
    && chown -R www-data:www-data /var/log/apache2 \
    && chown -R www-data:www-data /var/run/apache2

# Создание необходимых директорий
RUN mkdir -p /app/db /app/files /app/static/vendor \
    && chmod -R 755 /app/static \
    && chown -R www-data:www-data /app/static

# Копирование остальных файлов проекта
COPY . .

# Установка Python-зависимостей
RUN sed -n '/^\[python\]/,/^$/p' .requirements | grep "==" | \
    grep -v "^\[" | pip install --no-cache-dir -r /dev/stdin

# Настройка директории для статических файлов
RUN mkdir -p /app/staticfiles \
    && chown -R www-data:www-data /app/staticfiles \
    && chmod -R 755 /app/staticfiles

# Открытие порта для Apache
EXPOSE 80

# Запуск оболочки по умолчанию
CMD ["sh"]