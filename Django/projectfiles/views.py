from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from rest_framework import status
import rest_framework
from rest_framework.views import APIView, Response
from . import models
from . import serializers


# Create your views here.
class getAllProjectFiles(View):
    
    def get(self, request):

        # this one is getProjects(APIView)
        # projects = models.Project.objects.all().values()
        # response = Response(projects)

        # this one is getProjects(View)
        html = ""
        projectFiles = models.ProjectFile.objects.all()
        # Project.objects.filter()
        # Project.objects.get()
        # Project.objects.filter(id__lt = 7)
        for files in projectFiles:
            file_path = "" + str(files.project.file_path) + "/" + str(files.branch.name) + "/" + str(files.name)

            
            html += f"<h1>{files.name}</h1>"
            html += f"<p>{file_path}</p>"
        response = HttpResponse(html)

        # if doing templates use:
        # response = render()
        return response

class getProjectFiles(APIView):
    
    def get(self, request):

        # this one is getProjects(APIView)
        # projects = models.Project.objects.all().values()
        # response = Response(projects)

        # this one is getProjects(View)
        fileList = []
        curProj = request.session.get("curProjName", "")
        curBranch = request.session.get("curBranchName", "")
        projectFiles = models.ProjectFile.objects.filter(project=curProj).filter(branch=curBranch)
        # Project.objects.filter()
        # Project.objects.get()
        # Project.objects.filter(id__lt = 7)
        for files in projectFiles:
            file_path = "" + str(files.project.file_path) + "/" + str(files.branch.name) + "/" + str(files.name)
            file = {}
            file["name"] = files.name
            file["path"] = file_path
            fileList.append(file)
        return Response({"files":fileList})
    
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