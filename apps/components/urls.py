from django.urls import path
from . import views

app_name = 'components'

urlpatterns = [
    path('', views.component_list_view, name='list'),
    path('project/<uuid:project_id>/add/', views.component_create_view, name='create'),
    path('api/auto-save/', views.component_auto_save_api, name='auto_save_api'),
    path('<uuid:component_id>/delete/', views.component_delete_view, name='delete'),
    path('project/<uuid:project_id>/export-excel/', views.component_export_excel_view, name='export_excel'),
]
