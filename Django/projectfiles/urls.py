from django.urls import path
from . import views

urlpatterns = [
    path('', views.getAllProjectFiles.as_view(), name='GetAllProjectFiles'),
    path('get/', views.getProjectFiles.as_view(), name='GetProjectFiles'),
    path('create/', views.CreateFiles.as_view(), name='CreateFiles'),

    # S3 routes
    path('upload/', views.upload_file, name='file-upload'),
    path('download/<path:file_key>/', views.download_file, name='file-download'),
    path('list/<int:project_id>/', views.list_files, name='file-list'),
    path('delete/<path:file_key>/', views.delete_file, name='file-delete'),
    path('info/<path:file_key>/', views.file_info, name='file-info'),
]