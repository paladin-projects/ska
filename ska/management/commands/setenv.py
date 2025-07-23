"""
Команда Django для автоматической генерации переменных окружения.

Создает файл .env на основе шаблона .env.example, позволяя настроить:
- Очистку значения SECRET_KEY для последующей генерации
- Установку режима отладки (DEBUG)
"""

from django.core.management.base import BaseCommand
import os
import shutil
from pathlib import Path
import re


class Command(BaseCommand):
    help = 'Creates .env file from .env.example template'

    def add_arguments(self, parser):
        """
        Определяет аргументы командной строки.

        Args:
            parser: Парсер аргументов командной строки
        """
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Set DEBUG=True in created .env file',
        )

    def handle(self, *args, **options):
        """
        Обработчик команды.

        Выполняет:
        1. Проверку наличия файла шаблона
        2. Запрос на перезапись существующего файла
        3. Копирование и модификацию файла
        4. Очистку значения SECRET_KEY
        5. Настройку режима отладки

        Args:
            options: Опции командной строки
        """
        example_path = '.env.example'
        env_path = '.env'

        if not os.path.exists(example_path):
            self.stdout.write(self.style.ERROR(f'File {example_path} not found'))
            return

        if os.path.exists(env_path):
            overwrite = input('.env file already exists. Overwrite? (y/n): ')

            if overwrite.lower() != 'y':
                self.stdout.write(self.style.WARNING('Operation cancelled'))
                return

        try:
            # Копирование шаблона
            shutil.copy2(example_path, env_path)

            # Чтение и модификация файла
            env_file = Path(env_path)
            content = env_file.read_text()

            # Очистка поля SECRET_KEY
            content = re.sub(
                r'DJANGO_SECRET_KEY=.*',
                'DJANGO_SECRET_KEY=',
                content
            )

            # Переключение DEBUG, если необходимо
            if options['debug']:
                content = content.replace('DJANGO_DEBUG=False', 'DJANGO_DEBUG=True')
                debug_status = 'DEBUG=True'
            else:
                debug_status = 'DEBUG=False'

            # Запись обновленных данных
            env_file.write_text(content)

            self.stdout.write(
                self.style.SUCCESS(
                    f"File {env_path} successfully created \n"
                    f"Use 'python manage.py keygen' to generate SECRET_KEY"
                )
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating file: {str(e)}'))