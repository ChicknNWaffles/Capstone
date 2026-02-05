from django.urls import path
from . import views

urlpatterns = [
    path("projects/", views.projects),
    path("login/", views.login_api),
    path("signup/", views.signup_api),
    path("me/", views.me),

]
