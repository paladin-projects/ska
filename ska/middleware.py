"""
Общепроектные middleware-компоненты.

Содержит middleware-классы, используемые на уровне всего проекта
для обеспечения общей функциональности во всех приложениях.
"""

import os
from django.conf import settings
from django.urls import reverse_lazy


class BackgroundMiddleware:
    """
    Middleware для управления фоновыми изображениями страниц.

    Обеспечивает единую систему управления фонами для всех приложений проекта.
    Реализует механизм автоматического наследования фонов, при котором дочерние
    страницы наследуют фон родительской страницы, если для них не задан
    собственный фон.

    Пример:
        Если для '/self-assessment/' установлен фон 'self_assessment_bg.jpg',
        то все страницы вида '/self-assessment/hardware/',
        '/self-assessment/software/' и т.д. будут автоматически использовать
        этот же фон, если для них явно не указан другой.

    Attributes:
        backgrounds (dict): Словарь соответствия URL-путей и фоновых изображений
            для всех приложений проекта.
        default_bg (str): Имя файла фонового изображения по умолчанию,
            используемого при отсутствии специального фона.
    """

    def __init__(self, get_response):
        """
        Инициализация общепроектного middleware.

        Устанавливает соответствие между URL-путями и фоновыми изображениями
        для всех основных разделов проекта.

        Args:
            get_response: Следующий обработчик в цепочке middleware.
        """
        self.get_response = get_response
        self.backgrounds = {
            str(reverse_lazy('profile:main')): 'profile_bg.jpg',
            str(reverse_lazy('auth:login')): 'auth_bg.jpg',
            str(reverse_lazy('self_assessment')): 'self_assessment_bg.jpg',
            str(reverse_lazy('certificate_main')): 'certificate_bg.jpg',
            str(reverse_lazy('employee_evaluation_main')): 'employee_evaluation_bg.jpg',
        }
        self.default_bg = 'main_bg.jpg'

    def get_background_for_path(self, path):
        """
        Определяет фоновое изображение для заданного пути.

        Реализует иерархическую систему определения фонов:
        1. Проверяет наличие специального фона для конкретного URL
        2. Если не найден, ищет фон ближайшей родительской страницы
        3. Если ни один фон не найден, возвращает общий фон по умолчанию

        Args:
            path (str): URL-путь, для которого нужно определить фон

        Returns:
            str: Имя файла фонового изображения из общего каталога фонов
        """

        # Проверка точного совпадения пути
        if path in self.backgrounds:
            return self.backgrounds[path]

        # Поиск ближайшего родительского пути с фоном
        path_parts = path.rstrip('/').split('/')
        while path_parts:
            parent_path = '/'.join(path_parts) + '/'

            if parent_path in self.backgrounds:
                return self.backgrounds[parent_path]

            path_parts.pop()

        return self.default_bg

    def __call__(self, request):
        """
        Обработка запроса на уровне проекта.

        Добавляет к объекту запроса атрибут background_image,
        который содержит путь к соответствующему фоновому изображению
        относительно корня статических файлов.

        Args:
            request: Объект HTTP-запроса

        Returns:
            HttpResponse: Ответ от следующего обработчика в цепочке middleware
        """
        bg_name = self.get_background_for_path(request.path)
        request.background_image = f'/static/background/images/{bg_name}'
        return self.get_response(request)