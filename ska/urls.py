"""Конфигурация URL проекта"""

from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from main import views as main_views
from ska import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('control/', include('control.urls')),
    path('', main_views.main, name='main'),
    path('self-assessment/', include('self_assessment.urls')),
    path('certificate/', include('certificate.urls')),
    path('employee-evaluation/', include('employee_evaluation.urls')),
    path('auth/', include('authentication.urls', namespace='auth')),
    path('selection/', include('selection.urls')),
    path('profile/', include('profile.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
