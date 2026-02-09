from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView, Response
from . import models
from . import serializers

# Create your views here.
class getBranches(View):
    
    def get(self, request):

        html = ""
        branches = models.Branch.objects.all()
        # Project.objects.filter()
        # Project.objects.get()
        # Project.objects.filter(id__lt = 7)
        for branch in branches:
            html += f"<h1>{branch.name}</h1>"
            html += f"<p>{branch.pk}</p>"
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