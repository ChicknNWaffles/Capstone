from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView, Response
from . import serializers
from . import models
from . import serializers


# Create your views here.
class getFiles(View):
    
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
        response = HttpResponse(html)

        # if doing templates use:
        # response = render()
        return response
    
class CreateFiles(APIView):

    serializer_class = serializers.ProjectSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid()
        data = serializer.validated_data

        file = models.ProjectFile(
            name=data.get("name"),
        )
        file.save()

        response = {
            "success": True,
            "name": file.name,
        }

        return Response(response)