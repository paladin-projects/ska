from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from ska.decorators import role_required
from django.contrib.auth.models import User
from django.contrib import messages
from self_assessment.models import Department, Employees
from certificate.models import Certificate
import json


@login_required
@role_required(['admin'])
def admin_index(request):
    return redirect('control:statistics')


@login_required
@role_required(['admin'])
def statistics(request):

    try:
        # Извлечение данных
        departments_labels = list(Department.objects.values_list('name', flat=True))
        departments_values = list(Department.objects.annotate(count=Count('employees')).values_list('count', flat=True))

        context = {
            'total_employees': Employees.objects.exclude(role='admin').count(),
            'total_departments': Department.objects.count(),
            'total_certificates': Certificate.objects.count(),
            'departments_labels': json.dumps(departments_labels),
            'departments_values': json.dumps(departments_values)
        }

        return render(request, 'statistics.html', context)

    except Exception as e:
        print(f"Error in statistics view: {str(e)}")
        import traceback
        traceback.print_exc()
        messages.error(request, 'Произошла ошибка при загрузке статистики')
        return redirect('main')