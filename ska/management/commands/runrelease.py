"""
Команда Django для запуска приложения в релиз-режиме.

Запускает Django-приложение с использованием сервера Gunicorn,
применяя конфигурации из указанного файла настроек.
"""

from django.core.management.base import BaseCommand
import os
import sys
from pathlib import Path
import gunicorn.app.base


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    """
    Приложение Gunicorn для Django.

    Обеспечивает запуск Django-приложения через Gunicorn
    с поддержкой пользовательских конфигураций.
    """

    def __init__(self, app, options=None):
        """
        Инициализация приложения.

        Args:
            app: WSGI-приложение Django
            options: Словарь с настройками Gunicorn
        """
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        """Загрузка конфигураций из словаря options в конфигурацию Gunicorn"""
        config = {
            key: value for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }

        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        """Загрузка WSGI-приложения"""
        return self.application


class Command(BaseCommand):
    help = 'Runs Django application in release mode using Gunicorn server'

    def add_arguments(self, parser):
        """
        Определение аргументов командной строки.

        Args:
            parser: Парсер аргументов командной строки
        """
        parser.add_argument(
            '--config',
            help='Name of the config file in ska/management/release directory',
            default='gunicorn.conf.py'
        )

        parser.add_argument(
            '--reload',
            action='store_true',
            help='Enable auto-reload on code changes',
        )

    def handle(self, *args, **options):
        """
        Обработчик команды.

        Выполняет:
        1. Настройку путей и импорт конфигураций
        2. Проверку наличия необходимых файлов
        3. Запуск Gunicorn с указанными настройками

        Args:
            options: Опции командной строки
        """
        from django.core.wsgi import get_wsgi_application

        # Получение пути к основной директории
        base_dir = Path(__file__).resolve().parent.parent.parent

        # Проверка того, что текущая директория находится в Python path
        if str(base_dir) not in sys.path:
            sys.path.append(str(base_dir))

        # Создание конфигурационного пути
        config_dir = base_dir / 'management' / 'release'
        config_path = config_dir / options['config']

        # Проверка директории, содержащей конфигурации
        if not config_dir.exists():
            self.stdout.write(
                self.style.ERROR(f'Release config directory not found: {config_dir}')
            )
            return

        # Проверка конфигураций
        if not config_path.exists():
            self.stdout.write(
                self.style.ERROR(f'Config file not found: {config_path}')
            )
            return

        # Импортирование конфигураций
        import importlib.util
        spec = importlib.util.spec_from_file_location('gunicorn_config', config_path)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)

        # Получение переменных окружения
        gunicorn_config = {
            key: getattr(config, key)
            for key in dir(config)
            if not key.startswith('_') and key != 'os' and key != 'multiprocessing'
        }

        # Переопределение параметра перезагрузки, если он указан
        if options['reload']:
            gunicorn_config['reload'] = True

        self.stdout.write(self.style.SUCCESS('Starting release server...'))

        # Запуск gunicorn
        StandaloneApplication(
            get_wsgi_application(),
            gunicorn_config
        ).run()