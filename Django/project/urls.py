from django.urls import path
from . import views
from collaborator.views import getCollaborators
from projectbranch.views import getBranches

urlpatterns = [
    path('', views.getProjects.as_view(), name='GetProject'),
    path("getUserProjects/", views.getUserProjects.as_view(), name='GetUserProjects'),
    path('createProject/', views.CreateProject.as_view(), name='CreateProjectAlt'),
    path('create/', views.CreateProjectButWithSerializers.as_view(), name='CreateProjectButWithSerializers'),
    path('<int:project_id>/collaborators/', getCollaborators.as_view(), name='projectDetails'),
    path('<int:project_id>/collaborators/add', views.ProjectCollaboratorsListCreate.as_view(), name='addProjectCollaborators'),
    path('<int:project_id>/', getBranches.as_view(), name='viewBranches'),
    path('<int:project_id>/addbranch/', views.ProjectBranches.as_view(), name='addBranches'),
    path('<int:project_id>/delete/', views.DeleteProject.as_view(), name='deleteProject'),
]