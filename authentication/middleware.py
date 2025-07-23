"""
Компоненты аутентификации и авторизации.

Содержит middleware-классы для управления доступом к ресурсам проекта
на основе статуса аутентификации пользователей.
"""

from django.shortcuts import redirect
from django.conf import settings
from urllib.parse import urlparse
from django.urls import reverse_lazy


class AuthenticationMiddleware:
    """
    Middleware для управления доступом к защищенным ресурсам проекта.

    Обеспечивает единую систему контроля доступа для всех приложений проекта.
    Перенаправляет неаутентифицированных пользователей на страницу входа,
    сохраняя URL исходного запроса для возврата после успешной аутентификации.

    Реализует следующую логику доступа:
    - Публичные ресурсы (логин, регистрация, статика) доступны всем
    - Защищенные ресурсы требуют аутентификации
    - При попытке доступа к защищенному ресурсу происходит перенаправление
      на страницу входа с сохранением исходного URL

    Attributes:
        get_response: Следующий обработчик в цепочке middleware.
    """

    def __init__(self, get_response):
        """
        Инициализация middleware контроля доступа.

        Args:
            get_response: Следующий обработчик в цепочке middleware.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Обработка запроса для контроля доступа.

        Проверяет статус аутентификации пользователя и определяет необходимость
        перенаправления на страницу входа. Для неаутентифицированных пользователей:
        1. Проверяет, является ли запрошенный ресурс публичным
        2. Если ресурс защищенный, выполняет перенаправление на страницу входа
        3. Сохраняет исходный URL для возврата после аутентификации

        Args:
            request: Объект HTTP-запроса

        Returns:
            HttpResponse: Либо ответ от следующего обработчика для публичных ресурсов
                        и аутентифицированных пользователей, либо перенаправление
                        на страницу входа для защищенных ресурсов
        """

        if not request.user.is_authenticated:

            # Получение URL из settings.py
            static_url = settings.STATIC_URL.lstrip('/')
            media_url = settings.MEDIA_URL.lstrip('/')
            admin_url = getattr(settings, 'ADMIN_URL', 'admin/').lstrip('/')

            # Формирование списка публичных URL
            public_urls = [
                str(reverse_lazy('auth:login')).lstrip('/'),
                str(reverse_lazy('auth:registration')).lstrip('/'),
                static_url,
                media_url,
                admin_url,
            ]

            current_url = request.path_info.lstrip('/')

            # Нормализация URL
            if current_url and not current_url.endswith('/'):
                url_slash = current_url + '/'

            else:
                url_slash = current_url

            # Проверка прямого совпадения с публичными URL
            if any(url in (current_url, url_slash) for url in public_urls):
                return self.get_response(request)

            # Проверка префиксов
            if any(current_url.startswith(url) for url in [static_url, media_url, admin_url]):
                return self.get_response(request)

            # Формирование URL для перенаправления
            next_url = request.get_full_path()
            parsed_next = urlparse(next_url)

            # Проверка безопасности URL для перенаправления
            if (not parsed_next.netloc and
                    not parsed_next.scheme and
                    not next_url.startswith(str(reverse_lazy('auth:login'))) and
                    not any(next_url.startswith('/' + url) for url in public_urls)):
                login_url = f"{settings.LOGIN_URL}?next={next_url}"

            else:
                login_url = settings.LOGIN_URL

            return redirect(login_url)

        return self.get_response(request)