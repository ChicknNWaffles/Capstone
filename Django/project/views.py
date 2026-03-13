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
            html += f"<p>{project.repo_link}</p>"
            html += f"<p>{project.last_edited}</p>"
        response = HttpResponse(html)

        # if doing templates use:
        # response = render()
        return response


class getUserProjects(APIView):
    def get(self,request):
        user = request.user
        projects = models.Project.objects.filter(owner__username=user.username)
        projects = models.Project.objects.all()
        objs = []
        for project in projects:
            jsonObj = {}
            jsonObj["id"] = project.id
            jsonObj["name"] = project.name
            jsonObj["visibility"] = project.visibility
            jsonObj["path"] = project.file_path
            jsonObj["link"] = project.repo_link
            jsonObj["last_edited"] = project.last_edited
            objs.append(jsonObj)
        response = Response({"projects":objs})

        return response
    
class CreateProject(APIView):
        
    def post(self, request):
        user = request.user
        name = request.data.get("name")
        filepath = request.data.get("filepath")
        visibility = request.data.get("visibility")
        repoLink = request.data.get("repoLink")


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
            repo_link=repoLink,
        )
        project.save()

        response = {
            "success": True,
            "name": project.name,
            "filepath": project.file_path,
            "visibility": project.visibility,
            "repoLink":project.repo_link,
            "last_edited":project.last_edited,
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
            repo_link=data.get("repo_link"),
        )
        project.save()

        response = {
            "success": True,
            "name": project.name,
            "filepath": project.file_path,
            "visibility": project.visibility,
            "repoLink":project.repo_link,
            "last_edited":project.last_edited,
        }

        return Response(response)

class GetMainBranch(APIView):

    def get(self, request):
        pass