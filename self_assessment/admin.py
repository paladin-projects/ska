from django.contrib import admin
from django import forms
from .models import *


class EmployeesForm(forms.ModelForm):

    class Meta:
        model = Employees
        fields = ['user', 'name', 'department', 'role', 'subordinate_of']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.role in ['supervisor', 'admin']:
            self.fields['subordinate_of'].disabled = True
            self.fields['subordinate_of'].required = False


@admin.register(Employees)
class EmployeesAdmin(admin.ModelAdmin):
    form = EmployeesForm
    list_display = ('name', 'user', 'get_department', 'role', 'get_subordinate_of')
    list_filter = ('role',)
    search_fields = ('name', 'department__name', 'user__username')
    list_per_page = 20
    ordering = ('name',)

    def get_department(self, obj):
        return obj.department if obj.role != 'admin' else '-'

    get_department.short_description = 'Отдел'

    def get_subordinate_of(self, obj):
        if obj.role == 'employee':
            return obj.subordinate_of
        return '-'

    get_subordinate_of.short_description = 'Руководитель'

    class Media:
        js = ('js/employees_admin.js',)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(SkillsHW)
class SkillsHWAdmin(admin.ModelAdmin):
    list_display = ('employee', 'get_department', 'product', 'get_score')
    list_filter = ('employee__department', 'product')
    search_fields = ('employee__name', 'product__name')

    def get_department(self, obj):
        return obj.employee.department

    get_department.short_description = 'Отдел'
    get_department.admin_order_field = 'employee__department'

    def get_score(self, obj):
        return obj.get_score()

    get_score.short_description = 'Оценка'


@admin.register(SkillsSW)
class SkillsSWAdmin(admin.ModelAdmin):
    list_display = ('employee', 'get_department', 'product', 'get_score')
    list_filter = ('employee__department', 'product')
    search_fields = ('employee__name', 'product__name')

    def get_department(self, obj):
        return obj.employee.department

    get_department.short_description = 'Отдел'
    get_department.admin_order_field = 'employee__department'

    def get_score(self, obj):
        return obj.get_score()

    get_score.short_description = 'Оценка'


@admin.register(SkillsPR)
class SkillsPRAdmin(admin.ModelAdmin):
    list_display = ('employee', 'get_department', 'process', 'level')
    list_filter = ('employee__department', 'process')
    search_fields = ('employee__name', 'process__name')

    def get_department(self, obj):
        return obj.employee.department

    get_department.short_description = 'Отдел'
    get_department.admin_order_field = 'employee__department'

admin.site.register(Levels)
admin.site.register(Hardware)
admin.site.register(Software)
admin.site.register(Processes)
admin.site.register(TaskHW)
admin.site.register(TaskSW)