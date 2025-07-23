"""Методы для отображения и работы с данными блока authentication"""
import http

from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from self_assessment.models import Employees, Department
from django.urls import reverse


def main(request):

    if request.user.is_authenticated:
        next_url = request.GET.get('next', '/')
        return redirect(next_url)

    if request.method == "POST":
        username = request.POST.get("login")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)

        return HttpResponse(
            status=http.HTTPStatus.NOT_FOUND,
            content="Пользователь с таким логином/паролем не найден"
        )

    return render(request, "auth.html")


def registration(request):
    departments = [
        {'id': 'integration', 'name': 'Отдел системной интеграции', 'icon': 'bi-building'},
        {'id': 'service', 'name': 'Сервисный центр', 'icon': 'bi-tools'},
        {'id': 'project', 'name': 'Проектный отдел', 'icon': 'bi-kanban'},
        {'id': 'sales', 'name': 'Отдел продаж', 'icon': 'bi-cart'}
    ]

    if request.method == "POST":

        # Валидация данных
        try:
            if len(request.POST['username']) < 3:
                return HttpResponse(
                    status=http.HTTPStatus.BAD_REQUEST,
                    content="Имя пользователя должно содержать минимум 3 символа"
                )

            if len(request.POST['password']) < 8:
                return HttpResponse(
                    status=http.HTTPStatus.BAD_REQUEST,
                    content="Пароль должен содержать минимум 8 символов"
                )

            if request.POST['password'] != request.POST.get('re-password'):
                return HttpResponse(
                    status=http.HTTPStatus.BAD_REQUEST,
                    content="Пароли не совпадают"
                )

            # Создание пользователя
            user = User.objects.create_user(
                username=request.POST['username'],
                password=request.POST['password'],
                email=request.POST['email'],
                first_name=request.POST['first-name'],
                last_name=request.POST['last-name']
            )

            try:
                department = Department.objects.get_or_create(
                    name=get_department_name(request.POST['department'])
                )[0]

                employee = Employees.objects.create(
                    user=user,
                    name=f"{user.first_name} {user.last_name}",
                    department=department,
                    role='employee'
                )

                login(request, user)
                next_url = request.GET.get('next', '/')
                return redirect(next_url)

            except Department.DoesNotExist:
                user.delete()

                return HttpResponse(
                    status=http.HTTPStatus.BAD_REQUEST,
                    content="Выбранный отдел не существует"
                )

        except IntegrityError:

            if 'user' in locals():
                user.delete()

            return HttpResponse(
                status=http.HTTPStatus.BAD_REQUEST,
                content="Ошибка при создании пользователя: возможно, такой пользователь уже существует"
            )

        except Exception as e:

            if 'user' in locals():
                user.delete()

            return HttpResponse(
                status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                content=f"Произошла ошибка при регистрации: {str(e)}"
            )

    return render(request, "registration.html", {'departments': departments})


def get_department_name(department_code):
    departments = {
        'integration': 'Отдел системной интеграции',
        'service': 'Сервисный центр',
        'project': 'Проектный отдел',
        'sales': 'Отдел продаж'
    }

    return departments.get(department_code)


@login_required
def user_logout(request):
    """
    Производит закрытие пользовательской сессии
    :param request: Объект запроса
    :return: редирект на страницу входа
    """
    logout(request)
    return redirect(reverse('auth:login'))