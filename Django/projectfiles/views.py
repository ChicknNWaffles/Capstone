from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView, Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, parser_classes
from . import serializers
from . import models
from api.file_service import file_service


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
        curProj = request.session.get("curProj", "")
        curBranch = request.session.get("curCom", "")
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


# ============================================
# S3 File Upload/Download Views
# ============================================

@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_file(request):
    """Upload a file to S3. POST /files/upload/ — requires: file, project_id"""
    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

    project_id = request.data.get('project_id')
    if not project_id:
        return Response({'error': 'project_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        project_id = int(project_id)
    except ValueError:
        return Response({'error': 'project_id must be a number'}, status=status.HTTP_400_BAD_REQUEST)

    user_id = request.user.id if request.user.is_authenticated else 1

    result = file_service.upload_file(
        file_obj=uploaded_file,
        filename=uploaded_file.name,
        project_id=project_id,
        user_id=user_id
    )

    if result['success']:
        return Response(result, status=status.HTTP_201_CREATED)
    return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def download_file(request, file_key):
    """Get a pre-signed download URL. GET /files/download/<file_key>/"""
    from urllib.parse import unquote
    result = file_service.get_download_url(unquote(file_key))
    if result['success']:
        return Response(result)
    return Response(result, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def list_files(request, project_id):
    """List all files for a project. GET /files/list/<project_id>/"""
    result = file_service.list_files(project_id)
    if result['success']:
        return Response(result)
    return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['DELETE'])
def delete_file(request, file_key):
    """Delete a file from S3. DELETE /files/delete/<file_key>/"""
    from urllib.parse import unquote
    result = file_service.delete_file(unquote(file_key))
    if result['success']:
        return Response(result)
    return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def file_info(request, file_key):
    """Get metadata for a file. GET /files/info/<file_key>/"""
    from urllib.parse import unquote
    result = file_service.get_file_info(unquote(file_key))
    if result['success']:
        return Response(result)
    if result.get('error') == 'File not found':
        return Response(result, status=status.HTTP_404_NOT_FOUND)
    return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)