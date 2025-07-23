from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='selection'),
    path('disciplines/<str:product>/', views.get_disciplines, name='selection_disciplines'),
    path('employees/', views.get_employees, name='selection_employees'),
]