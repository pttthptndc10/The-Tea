from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    path('', views.session_list_view, name='list'),
    path('create/', views.session_create_view, name='create'),
    path('<uuid:session_id>/', views.session_detail_view, name='detail'),
    path('<uuid:session_id>/edit/', views.session_edit_view, name='edit'),
    path('<uuid:session_id>/toggle-status/', views.toggle_session_status_view, name='toggle_status'),
]
