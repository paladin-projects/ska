"""Настройки Django"""

import os
import sys
from pathlib import Path
from django.urls import reverse_lazy
from dotenv import load_dotenv
from termcolor import colored

# Пропуск проверки .env для команд управления окружением
ENVIRONMENT_MANAGEMENT_COMMANDS = ['keygen', 'setenv']
is_env_command = any(cmd in sys.argv for cmd in ENVIRONMENT_MANAGEMENT_COMMANDS)

BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_ROOT = BASE_DIR / 'files'

MEDIA_URL = 'files/'

ADMIN_URL = 'admin/'

LOGIN_URL = reverse_lazy('auth:login')

LOGIN_REDIRECT_URL = '/'

def get_secret_key():
    """Динамическое получение SECRET_KEY"""
    load_dotenv(override=True)
    return os.getenv('DJANGO_SECRET_KEY')

# Получение SECRET_KEY из переменных окружения
if is_env_command:
    load_dotenv(override=True)
    SECRET_KEY = 'tmp-key'

else:

    if not load_dotenv():
        print(colored(".env file not found", "red", attrs=["bold"]), file=sys.stderr)
        sys.exit(1)

    django_key = get_secret_key()
    if not django_key:
        print(colored("WARNING: DJANGO_SECRET_KEY is not set in .env file", "yellow", attrs=["bold"]), file=sys.stderr)
        print(colored("Using temporary key", "yellow", attrs=["bold"]), file=sys.stderr)
        print(colored("Use 'python manage.py keygen' to generate a permanent key", "yellow", attrs=["bold"]), file=sys.stderr)
        SECRET_KEY = 'tmp-key'

    else:
        SECRET_KEY = django_key

# Режим отладки
DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '*').split(',')

# Инициализация приложений
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
    'certificate',
    'employee_evaluation',
    'selection.apps.SelectionConfig',
    'self_assessment',
    'authentication',
    'profile',
    'django_bootstrap5',
    'control.apps.ControlConfig',
    'ska'
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'certificate.middleware.CertificateMiddleware',
    'authentication.middleware.AuthenticationMiddleware',
    'ska.middleware.BackgroundMiddleware',
]

ROOT_URLCONF = 'ska.urls'

# Шаблоны
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'ska.context_processors.user_role',
                'ska.context_processors.urls_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'ska.wsgi.application'


# Базы данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db' / 'db.sqlite3',
    }
}


# Валидация паролей
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Языковые настройки и локализация
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Статические файлы (css, JavaScript, Images)
STATIC_URL = '/static/'

# Директория для сбора статических файлов
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Дополнительные директории для поиска статических файлов
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Тип поля первичного ключа по умолчанию
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

