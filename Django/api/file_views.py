"""
File API Views for S3 Operations

Endpoints:
- POST   /api/files/upload/          - Upload a file
- GET    /api/files/download/<key>/  - Get download URL
- DELETE /api/files/delete/<key>/    - Delete a file
- GET    /api/files/list/<project_id>/ - List project files
- GET    /api/files/info/<key>/      - Get file info
"""

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt

from .file_service import file_service


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_file(request):
    """
    Upload a file to S3
    
    Required fields:
    - file: The file to upload
    - project_id: ID of the project
    
    Returns file metadata on success
    """
    # Get the uploaded file
    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return Response(
            {'error': 'No file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get project ID
    project_id = request.data.get('project_id')
    if not project_id:
        return Response(
            {'error': 'project_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        project_id = int(project_id)
    except ValueError:
        return Response(
            {'error': 'project_id must be a number'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Upload to S3
    result = file_service.upload_file(
        file_obj=uploaded_file,
        filename=uploaded_file.name,
        project_id=project_id,
        user_id=request.user.id
    )
    
    if result['success']:
        return Response(result, status=status.HTTP_201_CREATED)
    else:
        return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_download_url(request, file_key):
    """
    Get a pre-signed download URL for a file
    
    URL is valid for 1 hour by default
    """
    # URL decode the file_key (it may contain slashes)
    from urllib.parse import unquote
    file_key = unquote(file_key)
    
    result = file_service.get_download_url(file_key)
    
    if result['success']:
        return Response(result)
    else:
        return Response(result, status=status.HTTP_404_NOT_FOUND)


@csrf_exempt
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_file(request, file_key):
    """
    Delete a file from S3
    
    TODO: Add permission check to ensure user owns the file/project
    """
    from urllib.parse import unquote
    file_key = unquote(file_key)
    
    result = file_service.delete_file(file_key)
    
    if result['success']:
        return Response(result)
    else:
        return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_project_files(request, project_id):
    """
    List all files for a specific project
    """
    try:
        project_id = int(project_id)
    except ValueError:
        return Response(
            {'error': 'Invalid project_id'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    result = file_service.list_files(project_id)
    
    if result['success']:
        return Response(result)
    else:
        return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_file_info(request, file_key):
    """
    Get metadata for a specific file
    """
    from urllib.parse import unquote
    file_key = unquote(file_key)
    
    result = file_service.get_file_info(file_key)
    
    if result['success']:
        return Response(result)
    elif result.get('error') == 'File not found':
        return Response(result, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)