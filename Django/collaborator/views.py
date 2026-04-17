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

        html = ""
        collaborators = models.Collaborator.objects.filter(project=project_id)


        color_names = {
            "#dc3545": "Red",
            "#007bff": "Blue",
            "#28a745": "Green",
            "#ffc107": "Yellow",
            "#fd7e14": "Orange",
            "#e83e8c": "Pink",
            "#6610f2": "Purple",
            "#00cec9": "Light Blue",
        }
        
        for collaborator in collaborators:
            html += f"<h1>Name: {collaborator.user}</h1>"
            html += f"<p>Hours: {collaborator.hours}</p>"
            html += f"<p>Admin access: {collaborator.admin_perms}</p>"
            html += f"<p>Editor: {collaborator.edit_perms}</p>"
            color_hex = collaborator.color
            color_name = color_names.get(color_hex, "Unknown")
            html += f'''
                <p>
                    Color: 
                    <span style="background-color: {color_hex}; color: white; padding: 4px 12px; 
                                border-radius: 20px; font-weight: bold;">
                        {color_name}
                    </span>
                </p>
            '''
            
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
    
# colors to choose from 
COLOR_PALETTE = [
    "#007bff", "#28a745", "#ffc107", "#fd7e14",
    "#e83e8c", "#6610f2", "#00cec9",
]

def unique_color_per_project(project, user):
    # owner is always red
    if project.owner == user:
        return "#dc3545"

    # get all used colors (except owners)
    used_colors = set(
        models.Collaborator.objects.filter(project=project)
        .exclude(user=user)
        .values_list('color', flat=True)
    )

    # assigns first available color
    for color in COLOR_PALETTE:
        if color not in used_colors:
            return color