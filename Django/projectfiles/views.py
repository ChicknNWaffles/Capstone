from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView, Response
from . import models
from . import serializers


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
        for files in projectFiles:
            html += f"<h1>{files.name}</h1>"
            html += f"<p>{files.visibility}</p>"
            html += f"<p>{files.file_path}</p>"
            html += f"<p>{files.repo_link}</p>"
        response = HttpResponse(html)

        # if doing templates use:
        # response = render()
        return response
    
class CreateBranch(APIView):

    serializer_class = serializers.ProjectSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid()
        data = serializer.validated_data

        project = models.Project(
            name=data.get("name"),
        )
        project.save()

        response = {
            "success": True,
            "name": project.name,
        }

        return Response(response)