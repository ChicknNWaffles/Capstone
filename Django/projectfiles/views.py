from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView, Response
from . import models


# Create your views here.
class getProjectFiles(View):
    
    def get(self, request):

        # this one is getProjects(APIView)
        # projects = models.Project.objects.all().values()
        # response = Response(projects)

        # this one is getProjects(View)
        html = ""
        projectFiles = models.Project.objects.all()
        # Project.objects.filter()
        # Project.objects.get()
        # Project.objects.filter(id__lt = 7)
        for project in projectFiles:
            html += f"<h1>{project.name}</h1>"
            html += f"<p>{project.visibility}</p>"
            html += f"<p>{project.file_path}</p>"
            html += f"<p>{project.repo_link}</p>"
        response = HttpResponse(html)

        # if doing templates use:
        # response = render()
        return response