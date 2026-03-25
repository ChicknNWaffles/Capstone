from django.shortcuts import render # render is for templates
from django.views import View
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView, Response
from . import models
from . import serializers
from project.models import Project

# Create your views here.
class getCollaborators(View):
    
    def get(self, request, project_id):

        # this one is getProjects(APIView)
        # projects = models.Project.objects.all().values()
        # response = Response(projects)

        # this one is getProjects(View)
        html = ""
        collaborators = models.Collaborator.objects.all()
        # Project.objects.filter()
        # Project.objects.get()
        # Project.objects.filter(id__lt = 7)
        for collaborator in collaborators:
            html += f"<h1>{collaborator.hours}</h1>"
            html += f"<p>{collaborator.admin_perms}</p>"
            html += f"<p>{collaborator.edit_perms}</p>"
        response = HttpResponse(html)

        # if doing templates use:
        # response = render()
        return response
    
class CreateCollaborator(APIView):
        
    def post(self, request):
        username = request.user
        admin_perms = request.data.get("admin_perms")
        edit_perms = request.data.get("edit_perms")
        hours = request.data.get("hours")

        
        collaborator = models.Collaborator(
            username=username,
            admin_perms=admin_perms,
            edit_perms=edit_perms,
            hours=hours,
        )
        collaborator.save()

        response = {
            "success": True,
            "username": collaborator.username,
            "admin_perms": collaborator.admin_perms,
            "edit_perms": collaborator.edit_perms,
            "hours": collaborator.hours,
        }

        return Response(response)
    
class CreateCollaboratorButWithSerializers(APIView):

    serializer_class = serializers.CollaboratorSerializer
       
    def post(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid()
        data = serializer.validated_data

        collaborator = models.Collaborator(
            user=user,
            admin_perms=data.get("admin_perms"),
            edit_perms=data.get("edit_perms"),
            hours=data.get("hours"),
        )
        collaborator.save()

        response = {
            "success": True,
            "admin_perms": collaborator.admin_perms,
            "edit_perms": collaborator.edit_perms,
            "hours": collaborator.hours,
        }

        return Response(response)