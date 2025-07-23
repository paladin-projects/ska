"""
Конфигурация ASGI.
Предоставляет ASGI-приложение как переменную уровня модуля с именем ``application``.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ska.settings')

application = get_asgi_application()
