from django.urls import path
from . import views

urlpatterns = [
    path('', views.getProjects.as_view(), name='GetProject'),
    path("getUserProjects", views.getUserProjects.as_view(), name='GetUserProjects'),
    path('create/', views.CreateProject.as_view(), name='CreateProject'),
    path('createProject/', views.CreateProject.as_view(), name='CreateProjectAlt'),
    path('create2/', views.CreateProjectButWithSerializers.as_view(), name='CreateProjectButWithSerializers'),
]