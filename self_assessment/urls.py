"""Конфигурация URL для модуля self_assessment"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.SelfAssessmentView.as_view(), name='self_assessment'),
    path('hardware/', views.HardwareAssessmentView.as_view(), name='hardware_assessment'),
    path('software/', views.SoftwareAssessmentView.as_view(), name='software_assessment'),
    path('processes/', views.ProcessesAssessmentView.as_view(), name='processes_assessment'),
    path('validate_name/', views.validate_name, name='validate_name'),
    path('upload_assessment/', views.upload_assessment, name='upload_assessment'),
]
