from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls', namespace='dashboard')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('projects/', include('apps.projects.urls', namespace='projects')),
    path('tasks/', include('apps.tasks.urls', namespace='tasks')),
    path('components/', include('apps.components.urls', namespace='components')),
    path('purchases/', include('apps.purchases.urls', namespace='purchases')),
    path('reports/', include('apps.reports.urls', namespace='reports')),
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),
    path('placeholders/', include('apps.placeholders.urls', namespace='placeholders')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
