from django.urls import path
from . import views

urlpatterns = [
    path('', views.getCollaborators.as_view(), name='GetCollaborator'),
    path('create/', views.CreateCollaborator.as_view(), name='CreateCollaborator'),
    path('create2/', views.CreateCollaboratorButWithSerializers.as_view(), name='CreateCollaboratorButWithSerializers'),
]