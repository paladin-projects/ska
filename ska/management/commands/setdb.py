"""
Команда Django для настройки базы данных.

Основной функционал - инициализация БД из внешних источников.
Поддерживает управление резервными копиями.
"""

from django.core.management.base import BaseCommand
from django.db import connection
import os
import sys
import shutil
from datetime import datetime, timedelta
from termcolor import colored
import glob
from abc import ABC, abstractmethod


class DatabaseOperation(ABC):
    """Базовый класс для всех операций с базой данных"""

    def __init__(self, command_instance, internal_db_path, dry_run=False):
        self.cmd = command_instance
        self.internal_db_path = internal_db_path
        self.dry_run = dry_run

    def execute(self):
        """Шаблонный метод для выполнения операции"""

        if self.dry_run:
            self.cmd.stdout.write(self.cmd.style.WARNING(f'\nDRY-RUN: Simulating {self.get_operation_name()}\n'))

        try:
            self.validate()
            self.prepare()
            result = self.perform_operation()
            self.cleanup()
            return result

        except Exception as e:
            self.handle_error(e)
            return False

    @abstractmethod
    def get_operation_name(self):
        """Возвращает название операции"""
        pass

    @abstractmethod
    def validate(self):
        """Проверяет возможность выполнения операции"""
        pass

    @abstractmethod
    def prepare(self):
        """Подготавливает все необходимое для операции"""
        pass

    @abstractmethod
    def perform_operation(self):
        """Выполняет основную операцию"""
        pass

    def cleanup(self):
        """Выполняет очистку после операции"""
        pass

    def handle_error(self, error):
        """Обрабатывает ошибки операции"""
        self.cmd.stderr.write(
            self.cmd.style.ERROR(f'Error during {self.get_operation_name()}: {str(error)}')
        )


class InitializeDatabase(DatabaseOperation):
    """Операция инициализации базы данных"""

    def __init__(self, command_instance, internal_db_path, source_path, force=False, dry_run=False):
        super().__init__(command_instance, internal_db_path, dry_run)
        self.source_path = source_path
        self.force = force
        self.sql_content = None
        self.tables = None

    def get_operation_name(self):
        return "database initialization"

    def validate(self):

        if not os.path.exists(self.source_path):
            raise FileNotFoundError(f'Source file not found at {self.source_path}')

        if os.path.exists(self.internal_db_path) and not self.force:
            raise Exception('Database already exists. Use --force to overwrite.')

    def prepare(self):

        if self.dry_run:
            self.cmd.stdout.write(f'Would read source data from: {self.source_path}')
            self.cmd.stdout.write(f'Would initialize database at: {self.internal_db_path}')

            if os.path.exists(self.internal_db_path):
                self.cmd.stdout.write('Would overwrite existing database')

            self.cmd.stdout.write('Would execute SQL script to create tables')
            return

        # Создание директории для БД
        os.makedirs(os.path.dirname(self.internal_db_path), exist_ok=True)

        # Создание резервной копии если БД существует
        if os.path.exists(self.internal_db_path):
            BackupDatabase(self.cmd, self.internal_db_path, self.dry_run).execute()

        # Чтение SQL скрипта
        self.cmd.stdout.write('Reading source data...')
        with open(self.source_path, 'r', encoding='utf-8') as f:
            self.sql_content = f.read()

    def perform_operation(self):

        if self.dry_run:
            self.cmd.stdout.write('Would verify database initialization')
            self.cmd.stdout.write('Would check for created tables')
            return True

        self.cmd.stdout.write('Initializing internal database...')

        # Выполнение SQL скрипта
        with connection.cursor() as cursor:
            cursor.executescript(self.sql_content)

        # Проверка успешности инициализации
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            self.tables = cursor.fetchall()

        if not self.tables:
            raise Exception("No tables were created in the database")

        # Создание резервной копии после инициализации
        BackupDatabase(self.cmd, self.internal_db_path, self.dry_run).execute()

        self.cmd.stdout.write(self.cmd.style.SUCCESS('Successfully initialized database from source'))
        self.cmd.stdout.write(self.cmd.style.SUCCESS(f'Internal database location: {self.internal_db_path}'))
        self.cmd.stdout.write(self.cmd.style.SUCCESS(f'Number of tables initialized: {len(self.tables)}'))
        return True


class BackupDatabase(DatabaseOperation):
    """Операция создания резервной копии"""

    def __init__(self, command_instance, internal_db_path, dry_run=False, retention_days=None):
        super().__init__(command_instance, internal_db_path, dry_run)
        self.retention_days = retention_days
        self.backup_path = None

    def get_operation_name(self):
        return "backup creation"

    def validate(self):

        if not os.path.exists(self.internal_db_path):
            raise FileNotFoundError('Database file does not exist')

    def prepare(self):
        backup_dir = self.cmd.get_backup_dir(self.internal_db_path, self.dry_run)
        local_time = datetime.now().astimezone()
        backup_name = f"backup-{local_time.strftime('%Y%m%d_%H%M%S')}"
        self.backup_path = os.path.join(backup_dir, backup_name)

        if self.dry_run:
            self.cmd.stdout.write(f'Would create directory: {backup_dir}')
            self.cmd.stdout.write(f'Would create backup file: {self.backup_path}')
            self.cmd.stdout.write(f'Would copy {self.internal_db_path} → {self.backup_path}')

    def perform_operation(self):

        if self.dry_run:
            return self.backup_path

        shutil.copy2(self.internal_db_path, self.backup_path)
        self.cmd.stdout.write(self.cmd.style.SUCCESS(f'Created backup: {self.backup_path}'))

        if self.retention_days is not None:
            SetBackupRetention(
                self.cmd,
                self.internal_db_path,
                self.retention_days,
                os.path.basename(self.backup_path).replace('backup-', ''),
                self.dry_run
            ).execute()

        return self.backup_path

    def cleanup(self):

        if not self.dry_run and self.backup_path:
            CleanupOldBackups(
                self.cmd,
                self.internal_db_path,
                self.cmd.default_retention_days,
                self.dry_run
            ).execute()


class RestoreDatabase(DatabaseOperation):
    """Операция восстановления из резервной копии"""

    def __init__(self, command_instance, internal_db_path, backup_path, dry_run=False):
        super().__init__(command_instance, internal_db_path, dry_run)
        self.backup_path = backup_path
        self.temp_backup = None

    def get_operation_name(self):
        return "database restoration"

    def validate(self):

        if not os.path.exists(self.backup_path):
            raise FileNotFoundError(f'Backup file not found: {self.backup_path}')

    def prepare(self):

        if os.path.exists(self.internal_db_path):
            self.temp_backup = f"{self.internal_db_path}.temp-{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            if self.dry_run:
                self.cmd.stdout.write(f'Would create temporary backup: {self.temp_backup}')

            else:
                shutil.copy2(self.internal_db_path, self.temp_backup)

    def perform_operation(self):

        if self.dry_run:
            self.cmd.stdout.write(f'Would restore database:')
            self.cmd.stdout.write(f'  {self.backup_path} → {self.internal_db_path}')
            self.cmd.stdout.write('Would verify restored database')
            self.cmd.stdout.write('Would check for existing tables')
            return True

        # Восстановление из резервной копии
        shutil.copy2(self.backup_path, self.internal_db_path)
        self.cmd.stdout.write(self.cmd.style.SUCCESS('Successfully restored from backup'))

        # Проверка восстановленной БД
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            if not tables:
                raise Exception("Restored database appears to be empty")

        self.cmd.stdout.write(self.cmd.style.SUCCESS(f'Number of tables in restored database: {len(tables)}'))
        return True

    def handle_error(self, error):
        super().handle_error(error)

        # Восстановление из временной копии при ошибке
        if self.temp_backup and os.path.exists(self.temp_backup):
            self.cmd.stdout.write('Attempting to restore previous state...')

            try:
                shutil.copy2(self.temp_backup, self.internal_db_path)
                self.cmd.stdout.write(self.cmd.style.SUCCESS('Successfully restored previous state'))

            except Exception as restore_error:
                self.cmd.stderr.write(
                    self.cmd.style.ERROR(f'Failed to restore previous state: {str(restore_error)}')
                )


class DeleteBackup(DatabaseOperation):
    """Операция удаления резервных копий"""

    def __init__(self, command_instance, internal_db_path, backup_name=None, dry_run=False):
        super().__init__(command_instance, internal_db_path, dry_run)
        self.backup_name = backup_name
        self.backups = None

    def get_operation_name(self):
        return "backup deletion"

    def validate(self):
        self.backups = self.cmd.get_backups(self.internal_db_path, self.backup_name, self.dry_run)

        if not self.backups:
            raise Exception('No backup files found')

    def prepare(self):

        if self.dry_run:

            for backup in self.backups:
                self.cmd.stdout.write(f'Would delete backup: {backup}')

            self.cmd.stdout.write(f'Would remove {len(self.backups)} backup(s) in total')

    def perform_operation(self):

        if self.dry_run:
            return True

        removed_count = 0
        for backup in self.backups:

            try:
                os.remove(backup)
                removed_count += 1

            except OSError as e:
                self.cmd.stderr.write(
                    self.cmd.style.ERROR(f'Failed to remove backup {backup}: {str(e)}')
                )

        if removed_count > 0:
            self.cmd.stdout.write(
                self.cmd.style.SUCCESS(f'Successfully removed {removed_count} backup(s)')
            )

        return True


class SetBackupRetention(DatabaseOperation):
    """Операция установки срока хранения резервных копий"""

    def __init__(self, command_instance, internal_db_path, days, backup_name=None, dry_run=False):
        super().__init__(command_instance, internal_db_path, dry_run)
        self.days = days
        self.backup_name = backup_name
        self.backups = None

    def get_operation_name(self):
        return "setting backup retention"

    def validate(self):

        if self.days <= 0 and self.days != -1:
            raise ValueError('Days value must be positive or -1 for infinite retention')

        self.backups = self.cmd.get_backups(self.internal_db_path, self.backup_name, self.dry_run)
        if not self.backups:
            raise Exception('No backup files found')

    def prepare(self):

        if self.dry_run:
            self.cmd.stdout.write('Would update retention periods:')

    def perform_operation(self):

        if self.days == -1:
            return self._set_infinite_retention()

        return self._set_days_retention()

    def _set_infinite_retention(self):

        for backup in self.backups:

            if backup.endswith('.infinite'):
                continue

            try:
                new_name = f"{backup}.infinite"

                if self.dry_run:
                    self.cmd.stdout.write(f'Would mark backup for infinite retention:')
                    self.cmd.stdout.write(f'  {backup} → {new_name}')

                else:
                    os.rename(backup, new_name)
                    self.cmd.stdout.write(
                        self.cmd.style.SUCCESS(f'Marked backup for infinite retention: {new_name}')
                    )

            except OSError as e:
                self.cmd.stderr.write(
                    self.cmd.style.WARNING(f'Failed to mark backup {backup}: {str(e)}')
                )

        return True

    def _set_days_retention(self):

        for backup in self.backups:

            if backup.endswith('.infinite'):

                if self.dry_run:
                    self.cmd.stdout.write(f'Would skip infinite retention backup: {backup}')

                continue

            try:
                base_backup = backup

                if '.days-' in backup:
                    base_backup = backup.split('.days-')[0]

                new_name = f"{base_backup}.days-{self.days}"

                if self.dry_run:

                    if backup != new_name:
                        self.cmd.stdout.write(f'Would update retention period:')
                        self.cmd.stdout.write(f'  {backup} → {new_name}')

                    else:
                        self.cmd.stdout.write(f'Would keep existing retention period for: {backup}')

                else:

                    if backup != new_name:
                        os.rename(backup, new_name)

                    self.cmd.stdout.write(
                        self.cmd.style.SUCCESS(f'Set retention period of {self.days} days for backup: {new_name}')
                    )

            except OSError as e:
                self.cmd.stderr.write(
                    self.cmd.style.WARNING(f'Failed to set retention for backup {backup}: {str(e)}')
                )

        return True


class CleanupOldBackups(DatabaseOperation):
    """Операция очистки старых резервных копий"""

    def __init__(self, command_instance, internal_db_path, days_to_keep, dry_run=False):
        super().__init__(command_instance, internal_db_path, dry_run)
        self.days_to_keep = days_to_keep
        self.backups = None
        self.cutoff_date = None

    def get_operation_name(self):
        return "cleaning up old backups"

    def validate(self):
        backup_dir = self.cmd.get_backup_dir(self.internal_db_path, self.dry_run)
        backup_pattern = os.path.join(backup_dir, "backup-*")
        self.backups = glob.glob(backup_pattern)

        if not self.backups:
            return False

        self.cutoff_date = datetime.now() - timedelta(days=self.days_to_keep)
        return True

    def prepare(self):
        if self.dry_run:
            self.cmd.stdout.write('Would check backups for expiration:')

    def perform_operation(self):

        if not self.backups:
            return True

        removed_count = 0
        for backup in self.backups:

            if backup.endswith('.infinite'):

                if self.dry_run:
                    self.cmd.stdout.write(f'Would skip infinite retention backup: {backup}')

                continue

            try:
                base_name = os.path.basename(backup)
                timestamp = base_name.split('backup-')[1].split('.')[0]
                backup_date = datetime.strptime(timestamp, '%Y%m%d_%H%M%S')

                if backup_date < self.cutoff_date:

                    if self.dry_run:
                        self.cmd.stdout.write(f'Would remove old backup: {backup}')
                        removed_count += 1

                    else:
                        os.remove(backup)
                        removed_count += 1

                elif self.dry_run:
                    self.cmd.stdout.write(f'Would keep backup (not expired): {backup}')

            except (ValueError, OSError) as e:
                self.cmd.stderr.write(
                    self.cmd.style.WARNING(f'Failed to process backup {backup}: {str(e)}')
                )

        if removed_count > 0:
            message = f'Would remove {removed_count} old backup(s)' if self.dry_run else f'Removed {removed_count} old backup(s)'
            self.cmd.stdout.write(self.cmd.style.SUCCESS(message))

        return True


class ListBackups(DatabaseOperation):
    """Операция просмотра списка резервных копий"""

    def __init__(self, command_instance, internal_db_path, backup_name=None, dry_run=False):
        super().__init__(command_instance, internal_db_path, dry_run)
        self.backup_name = backup_name
        self.backups = None

    def get_operation_name(self):
        return "backup listing"

    def validate(self):
        self.backups = self.cmd.get_backups(self.internal_db_path, self.backup_name, self.dry_run)

        if not self.backups:
            raise Exception('No backup files found')

    def prepare(self):

        if self.dry_run:
            self.cmd.stdout.write(self.style.WARNING('DRY-RUN: Simulating backup listing'))

    def perform_operation(self):

        # Получение имени текущей БД
        current_db = os.path.splitext(os.path.basename(self.internal_db_path))[0]
        db_info = colored(f'[{current_db}]', 'blue')

        if self.backup_name == '-all' or self.backup_name is None:
            self.cmd.stdout.write(self.cmd.style.SUCCESS(f'Found {len(self.backups)} backup(s) for database {db_info}:'))

        elif self.backup_name == '-latest':
            self.cmd.stdout.write(self.cmd.style.SUCCESS(f'Latest backup for database {db_info}:'))

        else:
            self.cmd.stdout.write(self.cmd.style.SUCCESS(f'Backup details for database {db_info}:'))

        for backup in self.backups:

            if self.dry_run and not os.path.exists(backup):
                self.cmd.stdout.write(f'Would show details for: {backup}')
                continue

            backup_info = self.cmd.get_backup_info(backup, self.dry_run)
            self.cmd.stdout.write(f'- {backup_info}')

        return True


class Command(BaseCommand):
    help = 'Set up database from external source with backup management'
    default_retention_days = 30  # Срок хранения по умолчанию

    def add_arguments(self, parser):
        """
        Определение аргументов командной строки.

        Args:
            parser: Парсер аргументов командной строки
        """
        parser.add_argument(
            '--source',
            default='db/ska-init.sql',
            help='Path to source SQL file (default: db/ska-init.sql)'
        )
        parser.add_argument(
            '--db',
            default='db/db.sqlite3',
            help='Path to internal database (default: db/db.sqlite3)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force initialization even if database already exists'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making actual changes'
        )

        # Подпарсеры для работы с резервными копиями
        backup_parser = parser.add_argument_group('backup operations')
        backup_parser.add_argument(
            '--backup',
            nargs='?',
            const='create',
            help='Backup operations. Without additional arguments creates a new backup'
        )
        backup_parser.add_argument(
            '-latest',
            dest='latest',
            action='store_true',
            help='Use latest backup for operation'
        )
        backup_parser.add_argument(
            '-list',
            dest='list',
            nargs='?',
            const='',
            metavar='BACKUP',
            help='List backups. Without arguments shows latest backup, specific backup name or -all for all backups'
        )
        backup_parser.add_argument(
            '-delete',
            dest='delete',
            nargs='?',
            const='',
            metavar='BACKUP',
            help='Delete specified backup. Without arguments or with -latest deletes latest backup, with -all deletes all backups'
        )
        backup_parser.add_argument(
            '-restore',
            dest='restore',
            nargs='?',
            const='',
            metavar='BACKUP',
            help='Restore database from specified backup. Without arguments or with -latest restores from latest backup'
        )
        backup_parser.add_argument(
            '-days',
            dest='days',
            nargs='+',
            type=str,
            help=f'Set retention period: -days DAYS [BACKUP_NAME]. Without BACKUP_NAME creates new backup with specified retention. Use -1 for infinite retention. Default: {self.default_retention_days} days'
        )
        backup_parser.add_argument(
            '-all',
            dest='all',
            action='store_true',
            help='Apply operation to all existing backups'
        )

    def get_backup_dir(self, internal_db_path, dry_run=False):
        """
        Получение директории для хранения резервных копий.

        Args:
            internal_db_path: Путь к внутренней БД
            dry_run: Режим симуляции

        Returns:
            str: Путь к директории резервных копий
        """

        db_name = os.path.splitext(os.path.basename(internal_db_path))[0]
        backup_dir = os.path.join(os.path.dirname(internal_db_path), 'backups', db_name)

        if not dry_run:
            os.makedirs(backup_dir, exist_ok=True)

        return backup_dir

    def get_backup_path(self, internal_db_path, backup_name, dry_run=False):
        """
        Получение полного пути к резервной копии.

        Args:
            internal_db_path: Путь к внутренней БД
            backup_name: Имя резервной копии
            dry_run: Режим симуляции

        Returns:
            str: Полный путь к резервной копии
        """

        if os.path.isabs(backup_name):
            return backup_name

        backup_dir = self.get_backup_dir(internal_db_path, dry_run)

        if not backup_name.startswith('backup-'):
            return os.path.join(backup_dir, f"backup-{backup_name}")

        return os.path.join(backup_dir, backup_name)

    def get_backups(self, internal_db_path, backup_name=None, dry_run=False):
        """
        Получение списка резервных копий.

        Args:
            internal_db_path: Путь к внутренней БД
            backup_name: Имя конкретной резервной копии или None для всех копий
            dry_run: Режим симуляции

        Returns:
            list: Список путей к резервным копиям
        """

        backup_dir = self.get_backup_dir(internal_db_path, dry_run)

        if backup_name == '-all' or backup_name is None:

            # Получение всех копий (обычные, с установленным сроком и бессрочные)
            backup_pattern = os.path.join(backup_dir, "backup-*")
            backups = glob.glob(backup_pattern)

            # Сортировка по дате создания (без учета суффиксов)
            return sorted(backups,
                        key=lambda x: os.path.basename(x).split('backup-')[1].split('.')[0],
                        reverse=True)

        elif backup_name == '-latest':
            backup_pattern = os.path.join(backup_dir, "backup-*")
            backups = glob.glob(backup_pattern)

            # Сортировка по дате создания (без учета суффиксов)
            return [sorted(backups,
                         key=lambda x: os.path.basename(x).split('backup-')[1].split('.')[0],
                         reverse=True)[0]] if backups else []

        else:
            backup_path = self.get_backup_path(internal_db_path, backup_name, dry_run)
            base_path = backup_path.split('.days-')[0] if '.days-' in backup_path else backup_path

            # Проверяем все варианты - без суффикса, с суффиксом days и с суффиксом infinite
            if os.path.exists(base_path):
                return [base_path]

            # Поиск файла с любым суффиксом days-*
            matching_backups = glob.glob(f"{base_path}.days-*")
            if matching_backups:
                return [matching_backups[0]]

            # Проверка на бессрочное хранение
            if os.path.exists(f"{base_path}.infinite"):
                return [f"{base_path}.infinite"]

            return []

    def get_backup_info(self, backup_path, dry_run=False):
        """
        Получение информации о резервной копии.

        Args:
            backup_path: Путь к резервной копии
            dry_run: Режим симуляции

        Returns:
            str: Строка с информацией о копии
        """

        if dry_run and not os.path.exists(backup_path):
            return f"Would show info for: {backup_path}"

        try:
            size = os.path.getsize(backup_path) / 1024  # размер в КБ
            base_name = os.path.basename(backup_path)
            timestamp = base_name.split('backup-')[1].split('.')[0]
            backup_date = datetime.strptime(timestamp, '%Y%m%d_%H%M%S')
            age = datetime.now() - backup_date

            # Получение имени БД из пути к резервной копии
            db_name = os.path.basename(os.path.dirname(backup_path))
            db_info = colored(f'[{db_name}]', 'blue')

            info = f"{db_info} {timestamp} ({size:.1f} KB, {age.days} days old)"

            # Добавление информации о сроке хранения
            if backup_path.endswith('.infinite'):
                info += f" [{colored('infinite retention', 'cyan')}]"

            else:
                # Проверяем наличие пользовательского срока хранения
                retention_days = self.default_retention_days

                if '.days-' in backup_path:
                    retention_days = int(backup_path.split('.days-')[1])

                expiration_date = backup_date + timedelta(days=retention_days)
                days_left = (expiration_date - datetime.now()).days

                if days_left < 0:
                    retention_info = colored(f'{retention_days} days (expired)', 'red')
                    days_left = colored(str(days_left), 'red')

                elif days_left < 7:
                    retention_info = colored(f'{retention_days} days', 'yellow')
                    days_left = colored(str(days_left), 'yellow')

                else:
                    retention_info = colored(f'{retention_days} days', 'green')
                    days_left = colored(str(days_left), 'green')

                info += f" [retention: {retention_info}, days left: {days_left}]"

            return info

        except (ValueError, OSError, IndexError):
            return backup_path

    def confirm_operation(self, operation_type, details, dry_run=False):
        """
        Запрос подтверждения операции с выводом подробной информации.

        Args:
            operation_type: Тип операции ('delete' или 'restore')
            details: Словарь с деталями операции
            dry_run: Режим симуляции

        Returns:
            bool: True если операция подтверждена, False если отменена
        """

        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY-RUN: Simulating operation confirmation'))

        operation_name = 'Deletion' if operation_type == 'delete' else 'Restoration'

        self.stdout.write('\nOperation details:')
        self.stdout.write('=' * 50)
        self.stdout.write(f'Operation: {colored(operation_name, "yellow")}')

        if operation_type == 'delete':

            if details.get('is_all'):
                self.stdout.write(colored('WARNING: This will delete ALL backup files!', 'red'))

            elif details.get('is_latest'):
                self.stdout.write(f'Target: Latest backup ({details["backup_info"]})')

            else:
                self.stdout.write(f'Target backup: {details["backup_info"]}')


            if details.get('infinite'):
                self.stdout.write(colored('Note: This backup has infinite retention!', 'cyan'))

        else:  # restore

            if details.get('is_latest'):
                self.stdout.write(f'Source: Latest backup ({details["backup_info"]})')

            else:
                self.stdout.write(f'Source backup: {details["backup_info"]}')

            self.stdout.write(f'Target: {details["target_db"]}')
            if details.get('db_exists'):
                self.stdout.write(colored('Note: Target database will be overwritten!', 'yellow'))

            if details.get('infinite'):
                self.stdout.write(colored('Note: This is an infinite retention backup', 'cyan'))

        self.stdout.write('=' * 50)

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY-RUN: Would ask for confirmation'))
            return True

        try:
            response = input('\nDo you want to proceed? [y/N]: ').lower()
            return response == 'y'

        except KeyboardInterrupt:
            self.stdout.write('\nOperation cancelled by user')
            return False

    def handle(self, *args, **options):
        """
        Обработчик команды.

        Args:
            options: Опции командной строки
        """

        dry_run = options['dry_run']
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY-RUN MODE: No changes will be made\n'))

        internal_db_path = options['db']

        # Проверка аргументов
        has_explicit_args = (
            options['source'] != 'db/ska-init.sql' or
            options['db'] != 'db/db.sqlite3' or
            options['dry_run'] or
            options['backup'] is not None or
            any(options.get(opt) for opt in ['list', 'delete', 'restore', 'days'])
        )

        try:
            # Инициализация БД по умолчанию
            if not has_explicit_args:
                InitializeDatabase(
                    self, internal_db_path, options['source'],
                    options['force'], dry_run
                ).execute()
                return

            # Обработка операций с резервными копиями
            if options['backup'] is not None or any(options.get(opt) for opt in ['list', 'delete', 'restore', 'days']):

                # Создание директории для БД если её нет
                backup_dir = self.get_backup_dir(internal_db_path, dry_run)

                # Обработка списка резервных копий
                if options['list'] is not None:
                    target = '-latest'

                    if options['all']:
                        target = '-all'

                    elif options['list']:
                        target = options['list']

                    ListBackups(self, internal_db_path, target, dry_run).execute()
                    return

                # Обработка удаления резервных копий
                if options['delete'] is not None:
                    target = '-latest'

                    if options['delete']:
                        target = options['delete']

                    elif options['latest']:
                        target = '-latest'

                    elif options['all']:
                        target = '-all'

                    # Получение списка копий для удаления
                    backups = self.get_backups(internal_db_path, target, dry_run)
                    if not backups:
                        self.stderr.write(self.style.WARNING('No backup files found'))
                        return

                    # Подготовка информации для подтверждения
                    details = {
                        'is_all': target == '-all',
                        'is_latest': target == '-latest',
                        'backup_info': self.get_backup_info(backups[0], dry_run) if len(backups) == 1 else f'{len(backups)} backups',
                        'infinite': any(b.endswith('.infinite') for b in backups)
                    }

                    # Запрос подтверждения
                    if not self.confirm_operation('delete', details, dry_run):
                        self.stdout.write('Operation cancelled')
                        return

                    DeleteBackup(self, internal_db_path, target, dry_run).execute()
                    return

                # Обработка восстановления из резервной копии
                if options['restore'] is not None:
                    target = '-latest'

                    if options['restore']:
                        target = options['restore']

                    elif options['latest']:
                        target = '-latest'

                    elif options['all']:
                        self.stderr.write(self.style.ERROR('Cannot restore from all backups'))
                        return

                    # Получение пути к резервной копии
                    backups = self.get_backups(internal_db_path, target, dry_run)
                    if not backups:
                        self.stderr.write(self.style.WARNING('No backup files found'))
                        return

                    backup_path = backups[0]

                    # Подготовка информации для подтверждения
                    details = {
                        'is_latest': target == '-latest',
                        'backup_info': self.get_backup_info(backup_path, dry_run),
                        'target_db': internal_db_path,
                        'db_exists': os.path.exists(internal_db_path),
                        'infinite': backup_path.endswith('.infinite')
                    }

                    # Запрос подтверждение
                    if not self.confirm_operation('restore', details, dry_run):
                        self.stdout.write('Operation cancelled')
                        return

                    # Создание резервной копии перед восстановлением
                    BackupDatabase(self, internal_db_path, dry_run).execute()
                    RestoreDatabase(self, internal_db_path, backup_path, dry_run).execute()
                    return

                # Установка срока хранения резервных копий
                if options['days']:
                    try:
                        days = int(options['days'][0])

                        # Если указано только количество дней, создаем новую копию
                        if len(options['days']) == 1 and not options['latest'] and not options['all']:
                            backup = BackupDatabase(self, internal_db_path, dry_run, days)
                            backup.execute()
                            return

                        # Определение цели для установки срока хранения
                        target = '-latest'
                        if len(options['days']) > 1:
                            target = options['days'][1]

                        elif options['latest']:
                            target = '-latest'

                        elif options['all']:
                            target = '-all'

                        SetBackupRetention(self, internal_db_path, days, target, dry_run).execute()
                        return

                    except ValueError:
                        self.stderr.write(
                            self.style.ERROR('Days value must be a number')
                        )
                    return

                # Создание новой резервной копии (по умолчанию)
                if options['backup'] == 'create':
                    BackupDatabase(self, internal_db_path, dry_run).execute()
                    return

            # Инициализация БД с указанными параметрами
            InitializeDatabase(
                self, internal_db_path, options['source'],
                options['force'], dry_run
            ).execute()

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'ERROR: {str(e)}'))