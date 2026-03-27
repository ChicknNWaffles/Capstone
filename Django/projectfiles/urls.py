from django.urls import path
from . import views

urlpatterns = [
    path('', views.getAllProjectFiles.as_view(), name='GetAllProjectFiles'),
    path('get/', views.getProjectFiles.as_view(), name='GetProjectFiles'),
    path('create/', views.CreateFiles.as_view(), name='CreateFiles'),
    # fariza's change: route to turn file lock on or off
    path('lock/toggle/', views.ToggleFileLock.as_view(), name='ToggleFileLock'),
    # fariza's change: route to check if the password is correct
    path('lock/verify/', views.VerifyFilePassword.as_view(), name='VerifyFilePassword'),
    # fariza's change: route to read what is inside a file
    path('content/', views.ReadFileContent.as_view(), name='ReadFileContent'),
    # fariza's change: route to rename a file
    path('rename/', views.RenameFile.as_view(), name='RenameFile'),
    # fariza's change: route to delete a file from database and disk
    path('delete-file/', views.DeleteFile.as_view(), name='DeleteFilePermanently'),

    # S3 routes
    path('upload/', views.upload_file, name='file-upload'),
    path('download/<path:file_key>/', views.download_file, name='file-download'),
    path('list/<int:project_id>/', views.list_files, name='file-list'),
    path('delete/<path:file_key>/', views.delete_file, name='file-delete'),
    path('info/<path:file_key>/', views.file_info, name='file-info'),
]