"""Методы для отображения и работы с данными блока employee evaluation"""
import http
import json
import operator

from array import array
from typing import Dict, List, Union, Optional

from django.contrib.auth.decorators import login_required
from django.db.models import Q, QuerySet, Max, Avg
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from certificate.models import Certificate, CertificateCategory, CertificateSubCategory

from self_assessment.models import (
    Department,
    Employees,
    Levels,
    Hardware,
    Software,
    Processes,
    SkillsHW,
    SkillsSW,
    SkillsPR,
    TaskHW,
    TaskSW
)

HW_MAX_SCORE = 48
SW_MAX_SCORE = 20


def get_levels_values() -> Dict[str, int]:
    return {level["level"]: level["weight"] for level in Levels.objects.values()}


def get_products_data() -> Dict[str, QuerySet]:
    return {
        'hw_products': Hardware.objects.values_list('product', flat=True),
        'hw_tasks': TaskHW.objects.values_list('task', flat=True),
        'sw_products': Software.objects.values_list('product', flat=True),
        'sw_tasks': TaskSW.objects.values_list('task', flat=True),
        'processes': Processes.objects.values_list('process', flat=True)
    }


def get_certificate_data():
    """Получает данные о категориях сертификатов"""
    return {
        'categories': CertificateCategory.objects.values_list('category', flat=True),
        'subcategories': list(CertificateSubCategory.objects.values_list('subcategory', 'subcategory_of'))
    }


@login_required
def main(request):

    if request.method == "GET":

        try:
            employee = Employees.objects.get(user=request.user)
            employees_data = []

            if employee.role == 'admin':
                employees = Employees.objects.select_related('department').exclude(role='admin')

            else:
                employees = Employees.objects.select_related('department').exclude(
                    Q(role='admin') | Q(id=employee.id)
                )

            for emp in employees:
                hw_skills = list(SkillsHW.objects.filter(employee=emp))
                hw_skills.sort(key=lambda x: x.get_score(), reverse=True)
                hw_skills = hw_skills[:3]

                sw_skills = list(SkillsSW.objects.filter(employee=emp))
                sw_skills.sort(key=lambda x: x.get_score(), reverse=True)
                sw_skills = sw_skills[:3]

                pr_skills = list(SkillsPR.objects.filter(employee=emp))
                pr_skills.sort(key=lambda x: x.get_score(), reverse=True)
                pr_skills = pr_skills[:3]

                certificates = Certificate.objects.filter(employee=emp).order_by('-date')[:2]

                employee_data = {
                    'id': emp.id,
                    'name': emp.name,
                    'department': emp.department.name if emp.department else "Не указан",
                    'role': emp.role,
                    'top_skills': {
                        'hardware': [{'name': skill.product.product, 'score': skill.get_score()} for skill in
                                     hw_skills],
                        'software': [{'name': skill.product.product, 'score': skill.get_score()} for skill in
                                     sw_skills],
                        'processes': [{'name': skill.process.process, 'score': skill.get_score()} for skill in
                                      pr_skills]
                    },
                    'certificates': [
                        {
                            'name': cert.training_name,
                            'date': cert.date,
                            'category': cert.category.category
                        } for cert in certificates
                    ],
                    'total_certificates': Certificate.objects.filter(employee=emp).count(),
                    'average_scores': {
                        'hardware': SkillsHW.objects.filter(employee=emp).aggregate(Avg('level__weight'))[
                                        'level__weight__avg'] or 0,
                        'software': SkillsSW.objects.filter(employee=emp).aggregate(Avg('level__weight'))[
                                        'level__weight__avg'] or 0,
                        'processes': SkillsPR.objects.filter(employee=emp).aggregate(Avg('level__weight'))[
                                         'level__weight__avg'] or 0
                    }
                }
                employees_data.append(employee_data)

            data = {
                "employees": employees_data,
                "departments": Department.objects.all(),
                "is_admin": employee.role == 'admin',
                "skill_categories": {
                    "hardware": Hardware.objects.values_list('product', flat=True),
                    "software": Software.objects.values_list('product', flat=True),
                    "processes": Processes.objects.values_list('process', flat=True)
                }
            }

            if employee.role in ['supervisor', 'admin']:
                products_data = get_products_data()
                cert_data = get_certificate_data()
                levels = get_levels_values()

                data.update({
                    "filters": {
                        "hw": {
                            "products": products_data['hw_products'],
                            "tasks": products_data['hw_tasks']
                        },
                        "sw": {
                            "products": products_data['sw_products'],
                            "tasks": products_data['sw_tasks']
                        },
                        "processes": products_data['processes'],
                        "certificates": {
                            "categories": cert_data['categories'],
                            "subcategories": cert_data['subcategories']
                        },
                        "levels": levels.keys()
                    },
                    "max_scores": {
                        "hw": HW_MAX_SCORE,
                        "sw": SW_MAX_SCORE
                    }
                })

            return render(request, "employee_evaluation.html", data)

        except Employees.DoesNotExist:
            messages.error(request, 'Ошибка: профиль сотрудника не найден')
            return redirect('auth:logout')

    return HttpResponse(status=http.HTTPStatus.METHOD_NOT_ALLOWED)


@login_required
def about(request):
    employee_id = request.GET.get('id')
    employee = Employees.objects.select_related('department').get(id=employee_id)
    hw_data = []

    for product in Hardware.objects.all():
        latest_skill = (SkillsHW.objects
                        .filter(employee=employee, product=product)
                        .select_related('level')
                        .order_by('-time')
                        .first())
        if latest_skill:
            hw_data.append({
                'product': str(product),
                'score': latest_skill.get_score()
            })

    sw_data = []

    for product in Software.objects.all():
        latest_skill = (SkillsSW.objects
                        .filter(employee=employee, product=product)
                        .select_related('level')
                        .order_by('-time')
                        .first())
        if latest_skill:
            sw_data.append({
                'product': str(product),
                'score': latest_skill.get_score()
            })

    pr_data = []

    for process in Processes.objects.all():
        latest_skill = (SkillsPR.objects
                        .filter(employee=employee, process=process)
                        .select_related('level')
                        .order_by('-time')
                        .first())
        if latest_skill:
            pr_data.append({
                'product': str(process),
                'score': latest_skill.level.weight
            })

    sections = {
        'Hardware': hw_data,
        'Software': sw_data,
        'Processes': pr_data
    }

    max_weight = Levels.objects.aggregate(Max('weight'))['weight__max']

    section_max_scores = {
        'Hardware': max_weight,
        'Software': max_weight,
        'Processes': max_weight
    }

    context = {
        'employee': employee,
        'sections': sections,
        'section_max_scores': section_max_scores,
        'employee_id': employee_id
    }

    return render(request, 'employee_evaluation_about.html', context)


@login_required
def about_block(request) -> HttpResponse:

    if request.method != "GET":
        return HttpResponse(status=http.HTTPStatus.METHOD_NOT_ALLOWED)

    employee = Employees.objects.select_related('department').get(id=request.GET.get("id"))
    block = request.GET.get("block")
    data = {}

    match block:

        case "hw":
            hw_data = get_products_tasks_levels(SkillsHW, employee, get_products(employee, "hw"))
            data = {"data": hw_data, "long": True, "max_score": HW_MAX_SCORE}

        case "sw":
            sw_data = get_products_tasks_levels(SkillsSW, employee, get_products(employee, "sw"))
            data = {"data": sw_data, "long": True, "max_score": SW_MAX_SCORE}

        case "pr":
            pr_data = get_products_tasks_levels(SkillsPR, employee, get_products(employee, "pr"), False)
            data = {"data": pr_data, "long": False}

    data["employee"] = {
        "name": employee.name,
        "department": employee.department.name if employee.department else None,
        "is_supervisor": employee.is_supervisor
    }

    return render(request, "employee_evaluation_about_block.html", data)

@login_required
def reviews(request):

    if request.method == "GET":
        reviews_data = Reviews.objects.select_related(
            'reviewer',
            'reviewer__department',
            'reviewed',
            'reviewed__department'
        ).all()

        return render(request, "employee_evaluation_reviews.html", {"revs": reviews_data})

    return HttpResponse(status=http.HTTPStatus.METHOD_NOT_ALLOWED)


@login_required
def review(request):
    """
    Предоставляет ревью с указанным id
    :param request: Объект запроса
    :return: Текст ревью
    """
    if request.method == "GET":
        return JsonResponse({"data": Reviews.objects.filter(id=request.GET["id"]).values().first()["message"]})
    return HttpResponse(status=http.HTTPStatus.METHOD_NOT_ALLOWED)


@login_required
def delete_review(request, review_id):
    """
    Удаляет выбранное ревью
    :param request: Объект запроса
    :param review_id: id ревью
    :return: Код 200 если удаление прошло успешно
    """
    if request.method != "DELETE":
        return HttpResponse(status=http.HTTPStatus.METHOD_NOT_ALLOWED)

    obj = Reviews.objects.get(id=review_id)
    employee_id = Employees.objects.get(name=f"{request.user.first_name} {request.user.last_name}").id
    if obj.reviewer_id == employee_id:
        obj.delete()
        return HttpResponse(status=http.HTTPStatus.OK)

    return HttpResponse(status=http.HTTPStatus.FORBIDDEN, content="Нельзя удалить чужое ревью!")


@login_required
def upload_review(request):
    """
    Загружает ревью
    :param request: Объект запроса
    :return: Код 200 если загрузка успешна
    """
    if request.method != "POST":
        return HttpResponse(status=http.HTTPStatus.METHOD_NOT_ALLOWED)

    employee = (Employees.
                objects.
                filter(name=f'{request.user.first_name} {request.user.last_name}').
                values().
                first())

    data = request.POST

    if employee["id"] == data["rev_id"]:
        return HttpResponse(status=http.HTTPStatus.FORBIDDEN, content="Нельзя писать отзыв себе же")

    obj = Reviews(reviewer_id=employee["id"],
                  reviewed_id=data["rev_id"],
                  block=data["block"],
                  message=data["message"],
                  theme=data["theme"])

    obj.save()
    return HttpResponse(status=200)


@login_required
def get_subordinates(request):
    """
    Предоставляет список id сотрудников, являющихся подчиненными отправившего запрос
    :param request: Объект запроса
    :return: Список id подчиненных
    """
    employee = Employees.objects.get(name=f"{request.user.first_name} {request.user.last_name}")
    return JsonResponse(
        {"data": list(Employees.objects.filter(subordinate_of=employee.id).values_list('id', flat=True))})


@login_required
def subordinates_apply_filters(request):
    """
    Фильтрует подчиненных по запрошенным фильтрам
    :param request: Объект запроса
    :return: Список подчиненных прошедших фильтры или id фильтра, после которого фильтровать больше некого
    """
    if request.method != "POST":
        return HttpResponse(status=http.HTTPStatus.METHOD_NOT_ALLOWED)

    data = json.loads(request.POST.get("data"))
    filters = data["filters"]
    subordinates = list(Employees.objects.filter(id__in=data["subordinates"]).values())
    sub_to_remove = []
    data_for_table = {key: [] for key in data["subordinates"]}
    levels_val = get_levels_values()

    for _id in filters:
        _filter = filters[_id]
        if _filter["block"] in ["hw", "sw"]:
            if _filter["task"] != "Total":
                for index, subordinate in enumerate(subordinates):
                    try:
                        model = SkillsHW if _filter["block"] == "hw" else SkillsSW
                        obj = model.objects.get(
                            employee_id=subordinate["id"],
                            product=_filter["product"],
                            task=_filter["task"]
                        )

                        if compare_to_filter(
                            _filter["sign"],
                            levels_val[obj.level_id],
                            levels_val[_filter["value"]]
                        ):
                            data_for_table[subordinate["id"]].append(obj.level_id)
                            continue

                    except model.DoesNotExist:
                        pass

                    sub_to_remove.append(index)

            elif _filter["task"] == "Total":
                for index, subordinate in enumerate(subordinates):
                    model = SkillsHW if _filter["block"] == "hw" else SkillsSW
                    score = get_product_score(model, subordinate["id"], _filter["product"])

                    if compare_to_filter(_filter["sign"], score, int(_filter["value"])):
                        data_for_table[subordinate["id"]].append(score)
                        continue
                    sub_to_remove.append(index)

        elif _filter["block"] == "pr":
            for index, subordinate in enumerate(subordinates):
                try:
                    obj = SkillsPR.objects.get(
                        process=_filter["process"],
                        employee_id=subordinate["id"]
                    )
                    if compare_to_filter(
                        _filter["sign"],
                        levels_val[obj.level_id],
                        levels_val[_filter["value"]]
                    ):
                        data_for_table[subordinate["id"]].append(obj.level_id)
                        continue

                except SkillsPR.DoesNotExist:
                    pass

                sub_to_remove.append(index)

        elif _filter["block"] == "cr":
            certificates = Certificate.objects.filter(category=_filter["category"])
            if _filter["subcategory"] != "any":
                certificates = certificates.filter(sub_category=_filter["subcategory"])

            for index, subordinate in enumerate(subordinates):
                if certificates.filter(employee_id=subordinate["id"]).exists():
                    subcategory = certificates.filter(employee_id=subordinate["id"]).first().sub_category
                    data_for_table[subordinate["id"]].append(str(subcategory) if subcategory else "N/A")
                    continue

                sub_to_remove.append(index)

        if sub_to_remove:
            subordinates = [subordinates[i] for i, _ in enumerate(subordinates) if i not in sub_to_remove]
            sub_to_remove.clear()

        if not subordinates:
            return HttpResponse(status=http.HTTPStatus.NOT_FOUND, content=_id)

    return JsonResponse(
        status=http.HTTPStatus.OK,
        data={
            "employees_id": [subordinate["id"] for subordinate in subordinates],
            "data_for_table": data_for_table
        }
    )


def get_products(employee: Employees, key="all"):
    """
    Возвращает список продуктов или процессов из базы данных

    :param employee: Объект БД, представляющий работника
    :param key: Ключ, ["all","hw","sw","pr"], в зависимости от него возвращаются продукты или процессы разных блоков
    :return: Массив(ы) строк
    """
    if key == "all":
        return (SkillsHW.
                objects.
                filter(employee_id=employee.id).values_list("product_id", flat=True).
                distinct(),
                SkillsSW.
                objects.
                filter(employee_id=employee.id).values_list("product_id", flat=True).
                distinct(),
                SkillsPR.
                objects.
                filter(employee_id=employee.id).values_list("process_id", flat=True).
                distinct())
    if key == "hw":
        return (SkillsHW.
                objects.
                filter(employee_id=employee.id).values_list("product_id", flat=True).
                distinct())
    if key == "sw":
        return (SkillsSW.
                objects.
                filter(employee_id=employee.id).values_list("product_id", flat=True).
                distinct())
    if key == "pr":
        return (SkillsPR.
                objects.
                filter(employee_id=employee.id).values_list("process_id", flat=True).
                distinct())

    return None


def get_products_scores(db_object: type[SkillsHW | SkillsSW | SkillsPR], employee: Employees,
                        product_list: array, is_long=True):
    """
    Возвращает массив словарей, где 1 словарь - 1 продукт или процесс и его суммарный уровень

    :param db_object: Объект БД, представляющий таблицу с компетенциями сотрудников по блоку
    :param employee: Объект БД, представляющий работника
    :param product_list: Список продуктов или процессов, для которых нужно собрать информацию
    :param is_long: Ключ, определяющий по какому шаблону будет составлен итоговый массив.
        True - у каждой дисциплины есть суб-дисциплины, а у них уже уровни.
        False - у дисциплины есть только ее собственный уровень.
    :return: Массив словарей формата [{"product", "score"}, ...] | [{"process", "level"}, ...]
    """
    arr = []
    if is_long:
        for product in product_list:
            arr.append({"product": product, "score": get_product_score(db_object, employee.id, product)})
    else:
        for process in product_list:
            data = (SkillsPR.
                    objects.
                    filter(employee_id=employee.id, process_id=process).
                    values_list("level_id", flat=True))
            arr.append({"process": process, "level": data[0]})
    return arr


def get_product_score(db_object: type[SkillsHW | SkillsSW | SkillsPR], employee_id, product):
    """
    Считает суммарное значение, представляющее общие знания о дисциплине
    """
    data = (db_object.
            objects.
            filter(employee_id=employee_id, product_id=product).
            values_list("level_id", flat=True))
    levels_val = get_levels_values()
    score = 0
    for i in data:
        score += levels_val[i]
    return score


def get_products_tasks_levels(db_object, employee, product_list, is_long=True):
    """
    Возвращает массив словарей, где 1 словарь - 1 продукт,
    его подкатегории и их уровни, либо же 1 процесс и его уровень

    :param db_object: Объект БД, представляющий таблицу с компетенциями сотрудников по блоку
    :param employee: Объект БД, представляющий работника
    :param product_list: Список продуктов или процессов, для которых нужно собрать информацию
    :param is_long: Ключ, определяющий по какому шаблону будет составлен итоговый массив
    :return: Словари формата [{"product", [("task", "level")...]}, ...] | [{"process", "level"}, ...]
    """
    arr = []
    if is_long:
        for product in product_list:
            data = (db_object.
                    objects.
                    filter(employee_id=employee.id, product_id=product).
                    values_list("task_id", "level_id"))
            tasks = []
            for i in data:
                tasks.append((i[0], i[1]))
            arr.append({"product": product, "tasks": tasks})
    else:
        for process in product_list:
            data = (SkillsPR.
                    objects.
                    filter(employee_id=employee.id, process_id=process).
                    values_list("level_id", flat=True))
            arr.append({"process": process, "level": data[0]})

    return arr


def compare_to_filter(sign: str, val1: int, val2: int) -> bool:
    """
    Сравнивает значения по нужному знаку.
    :param sign: Знак
    :param val1: Число 1
    :param val2: Число 2
    :return: True - знак корректен. False - знак некорректен
    """
    operators = {
        '<': operator.lt,
        '>': operator.gt,
        '=': operator.eq,
    }
    return operators.get(sign)(val1, val2)
