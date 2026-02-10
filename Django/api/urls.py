from django.urls import path
from . import views

urlpatterns = [
    path("projects/", views.projects),
    path("login/", views.login_api),
    path("signup/", views.signup_api),
    path("me/", views.me),

    # access project variable
    path("getProjName", views.getProjName),
    path("getComName", views.getComName),
    
    # URL to open a project
    path("open-project/<int:project_id>/", views.open_project), 
]
