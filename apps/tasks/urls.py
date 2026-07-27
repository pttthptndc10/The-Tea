from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list_view, name='list'),
    path('create/', views.task_create_view, name='create'),
    path('<uuid:task_id>/', views.task_detail_view, name='detail'),
    path('<uuid:task_id>/edit/', views.task_edit_view, name='edit'),
    path('<uuid:task_id>/update-status/', views.task_update_status_view, name='update_status'),
    path('<uuid:task_id>/cancel/', views.task_cancel_view, name='cancel'),
    path('<uuid:task_id>/delete/', views.task_delete_view, name='delete'),
    path('<uuid:task_id>/inline-edit/', views.task_inline_edit_view, name='inline_edit'),
    path('api/auto-save/', views.task_auto_save_api, name='auto_save_api'),
    path('project/<uuid:project_id>/quick-create/', views.task_quick_create_view, name='quick_create'),
]
