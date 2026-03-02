from django.urls import path
from . import views
from collaborator.views import getCollaborators

urlpatterns = [
    path('', views.getProjects.as_view(), name='GetProject'),
    path('create/', views.CreateProject.as_view(), name='CreateProject'),
    path('create2/', views.CreateProjectButWithSerializers.as_view(), name='CreateProjectButWithSerializers'),
    path('<int:project_id>/', getCollaborators.as_view(), name='GetCollaborator' ),
    path('<int:project_id>/collaborator/', views.ProjectCollaboratorsListCreate.as_view(), name='projectCollaborators'),
]