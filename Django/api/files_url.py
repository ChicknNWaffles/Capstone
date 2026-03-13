"""
URL Configuration for File API

Add these URLs to your main urls.py or include them:

    path('api/files/', include('api.file_urls')),
"""

from django.urls import path
from . import file_views

urlpatterns = [
    # Upload a file
    path('upload/', file_views.upload_file, name='file-upload'),
    
    # Get download URL for a file
    path('download/<path:file_key>/', file_views.get_download_url, name='file-download'),
    
    # Delete a file
    path('delete/<path:file_key>/', file_views.delete_file, name='file-delete'),
    
    # List files for a project
    path('list/<int:project_id>/', file_views.list_project_files, name='file-list'),
    
    # Get file info/metadata
    path('info/<path:file_key>/', file_views.get_file_info, name='file-info'),
]