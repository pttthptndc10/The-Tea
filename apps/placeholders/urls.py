from django.urls import path
from . import views

app_name = 'placeholders'

urlpatterns = [
    path('video-meeting/', views.video_meeting_placeholder, name='video_meeting'),
    path('inventory/', views.inventory_placeholder, name='inventory'),
    path('pdf-export/', views.pdf_export_placeholder, name='pdf_export'),
    path('file-storage/', views.file_storage_placeholder, name='file_storage'),
]
