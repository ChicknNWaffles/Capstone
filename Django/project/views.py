from django.shortcuts import render # render is for templates
from django.views import View
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView, Response
from . import models
from . import serializers

# Create your views here.



class getProjects(View):
    
    def get(self, request):

        # this one is getProjects(APIView)
        # projects = models.Project.objects.all().values()
        # response = Response(projects)

        # this one is getProjects(View)
        html = ""
        projects = models.Project.objects.all()
        # Project.objects.filter()
        # Project.objects.get()
        # Project.objects.filter(id__lt = 7)
        for project in projects:
            html += f"<h1>{project.name}</h1>"
            html += f"<p>{project.visibility}</p>"
            html += f"<p>{project.file_path}</p>"
        response = HttpResponse(html)

        # if doing templates use:
        # response = render()
        return response
    
class CreateProject(APIView):
        
    def post(self, request):
        user = request.user
        name = request.data.get("name")
        filepath = request.data.get("filepath")
        visibility = request.data.get("visibility")


        # example of a guard
        # check for name
        if name is None:
            response = {
                "success": False,
                "message": "User must provide project name"
            }
            return Response(response, status=status.HTTP_204_NO_CONTENT)

        # check for filespath
        if filepath is None:
            response = {
                "success": False,
                "message": "User must provide info about filepath"
            }
            return Response(response, status=status.HTTP_204_NO_CONTENT)
        
        # check for visibility
        if visibility is None:
            response = {
                "success": False,
                "message": "User must provide info about visibility"
            }
            return Response(response, status=status.HTTP_204_NO_CONTENT)
        
        project = models.Project(
            name=name,
            visibility=visibility,
            file_path=filepath,
            owner=user,
        )
        project.save()

        response = {
            "success": True,
            "name": project.name,
            "filepath": project.file_path,
            "visibility": project.visibility
        }

        return Response(response)
    
class CreateProjectButWithSerializers(APIView):

    serializer_class = serializers.ProjectSerializer
    
    def post(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid()
        data = serializer.validated_data

        project = models.Project(
            name=data.get("name"),
            visibility=data.get("visibility"),
            file_path=data.get("file_path"),
            owner=user,

        )
        project.save()

        response = {
            "success": True,
            "name": project.name,
            "filepath": project.file_path,
            "visibility": project.visibility
        }

        return Response(response)