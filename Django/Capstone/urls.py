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
from django.http import JsonResponse, HttpResponse
from django.template import loader
# fariza's change: ensure_csrf_cookie makes sure the browser always gets a CSRF token when loading the homepage
from django.views.decorators.csrf import ensure_csrf_cookie

# fariza's change: added @ensure_csrf_cookie so the browser gets the CSRF cookie needed to create projects
@ensure_csrf_cookie
def homePage(request):
    template = loader.get_template("homepage.html")
    return HttpResponse(template.render())

def loginPage(request):
    template = loader.get_template("login.html")
    return HttpResponse(template.render())

def signupPage(request):
    template = loader.get_template("signup.html")
    return HttpResponse(template.render())

def editorPage(request):
    template = loader.get_template("editor.html")
    return HttpResponse(template.render())

# fariza's change: function to render the new settings page
def settingsPage(request):
    template = loader.get_template("settings.html")
    return HttpResponse(template.render())


urlpatterns = [
    # render pages
    path("", homePage),
    path("login/", loginPage),
    path("signup/", signupPage),
    path("editor/", editorPage),
    # fariza's change: setting up the url path for the settings page
    path("settings/", settingsPage),

    # admin pages
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('project/', include('project.urls')),
    path('api/', include('api.urls')),
    path('collaborator/', include('collaborator.urls')),
    path('branch/', include('projectbranch.urls')),
    path('files/', include('projectfiles.urls')),
]
