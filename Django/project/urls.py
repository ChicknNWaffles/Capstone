from django.urls import path
from . import views
from collaborator.views import getCollaborators
from projectbranch.views import getBranches

urlpatterns = [
    path('', views.getProjects.as_view(), name='GetProject'),
    path("getUserProjects/", views.getUserProjects.as_view(), name='GetUserProjects'),
    path('create/', views.CreateProjectButWithSerializers.as_view(), name='CreateProjectButWithSerializers'),
    path('<int:project_id>/', getCollaborators.as_view(), name='projectDetails'),
    path('<int:project_id>/collaborators/', views.ProjectCollaboratorsListCreate.as_view(), name='addProjectCollaborators'),
    path('<int:project_id>/branches/', getBranches.as_view(), name='viewBranches'),
    path('<int:project_id>/branches/add', views.ProjectBranches.as_view(), name='addBranches'),
]