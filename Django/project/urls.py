from django.urls import path
from . import views

urlpatterns = [
    path('', views.getProjects.as_view(), name='GetProject'),
    path('create/', views.CreateProject.as_view(), name='CreateProject'),
    path('create2/', views.CreateProjectButWithSerializers.as_view(), name='CreateProjectButWithSerializers'),
]