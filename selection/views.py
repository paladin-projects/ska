from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from self_assessment.models import Hardware, Software, Processes, TaskHW, TaskSW, SkillsHW, SkillsSW, SkillsPR, \
    Employees


@login_required
def main(request):
    return render(request, "selections.html")


@login_required
def get_disciplines(request, product):
    """
    Возвращает список дисциплин для выбранного продукта
    """
    if product.startswith('HW_'):
        disciplines = TaskHW.objects.filter(product__product=product[3:]).values_list('task', flat=True)
    elif product.startswith('SW_'):
        disciplines = TaskSW.objects.filter(product__product=product[3:]).values_list('task', flat=True)
    else:
        disciplines = []

    return JsonResponse(list(disciplines), safe=False)


@login_required
def get_employees(request):
    """
    Возвращает список сотрудников, соответствующих критериям поиска
    """
    product = request.GET.get('product')
    discipline = request.GET.get('discipline')
    level = request.GET.get('level')

    if not all([product, discipline, level]):
        return JsonResponse([], safe=False)

    if product.startswith('HW_'):
        skills = SkillsHW.objects.filter(
            product__product=product[3:],
            task__task=discipline,
            level__weight=level
        ).select_related('employee')
    elif product.startswith('SW_'):
        skills = SkillsSW.objects.filter(
            product__product=product[3:],
            task__task=discipline,
            level__weight=level
        ).select_related('employee')
    else:
        skills = SkillsPR.objects.filter(
            process__process=product,
            level__weight=level
        ).select_related('employee')

    employees = [
        {
            'id': skill.employee.id,
            'name': skill.employee.name,
            'level': skill.level.level
        }
        for skill in skills
    ]

    return JsonResponse(employees, safe=False)
