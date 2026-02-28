from django.urls import path
from . import views

urlpatterns = [
    path('', views.getAllProjectFiles.as_view(), name='GetAllProjectFiles'),
    path('get/', views.getProjectFiles.as_view(), name='GetProjectFiles'),
    path('create/', views.CreateBranch.as_view(), name='CreateBranch'),
]