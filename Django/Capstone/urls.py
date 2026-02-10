"""
URL configuration for Capstone project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
# we need render so it passes the request info (like the csrf token) to the html
from django.shortcuts import render

def homePage(request):
    # render the homepage
    return render(request, "homepage.html")

def loginPage(request):
    # use render to make sure the csrf token gets sent to the template
    return render(request, "login.html")

def signupPage(request):
    # same here, need render for the form security
    return render(request, "signup.html")

def editorPage(request):
    return render(request, "editor.html")


urlpatterns = [
    # render pages
    path("", homePage),
    path("login/", loginPage),
    path("signup/", signupPage),
    path("editor/", editorPage),

    # admin pages
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('project/', include('project.urls')),
    path('api/', include('api.urls')),
    path('collaborator/', include('collaborator.urls')),
    path('branch/', include('projectbrach.urls')),
    # path('files/', include('projectfiles.urls')),



]
