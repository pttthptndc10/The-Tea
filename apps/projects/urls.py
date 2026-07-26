from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list_view, name='list'),
    path('create/', views.project_create_view, name='create'),
    path('<uuid:project_id>/', views.project_detail_view, name='detail'),
    path('<uuid:project_id>/edit/', views.project_edit_view, name='edit'),
    path('<uuid:project_id>/delete/', views.project_delete_view, name='delete'),
    path('<uuid:project_id>/assign-manager/', views.assign_manager_view, name='assign_manager'),
]
