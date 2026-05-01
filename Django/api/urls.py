from django.urls import path
from . import views

urlpatterns = [
    path("projects/", views.projects),
    path("login/", views.login_api),
    path("signup/", views.signup_api),
    path("me/", views.me),
    path("myCreds/", views.myCreds),

    path("getProjName", views.getProjName),
    path("getComName", views.getComName),
    path("setCurProj/", views.setCurProj),
    path("setCurBranch/", views.setCurBranch),
    # fariza's change: route to update project name, visibility, and repo link
    path("update-project-settings/", views.updateProjectSettings),
]
