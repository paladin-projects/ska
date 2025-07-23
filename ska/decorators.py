"""Конфигурация декораторов проекта"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from self_assessment.models import Employees

def role_required(roles):

    def decorator(view_func):
        """
        Декоратор для проверки роли пользователя.

        Проверяет наличие у пользователя необходимой роли для доступа к представлению.
        Если роль не соответствует требуемой, перенаправляет на главную страницу.
        Если профиль сотрудника не найден, осуществляет выход из системы.

        Args:
            roles: Список разрешенных ролей

        Returns:
            Функция-обертка для проверки роли
        """
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):

            try:
                employee = Employees.objects.get(user=request.user)

                if employee.role in roles:
                    return view_func(request, *args, **kwargs)

                else:
                    messages.error(request, 'Ошибка: недостаточно прав для доступа')
                    return redirect('main')

            except Employees.DoesNotExist:
                messages.error(request, 'Ошибка: профиль сотрудника не найден')
                return redirect('auth:logout')

        return _wrapped_view

    return decorator