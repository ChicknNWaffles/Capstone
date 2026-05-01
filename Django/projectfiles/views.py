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
from django.contrib.auth.hashers import make_password, check_password
import os # fariza's change: added os to read files from the computer's disk


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
        fileList = []
        curProj = request.session.get("curProj", "")
        curBranch = request.session.get("curCom", "")

        # Guard: if no project/branch selected yet, return empty list instead of crashing
        if not curProj or not curBranch:
            return Response({"files": fileList})

        projectFiles = models.ProjectFile.objects.filter(project=curProj).filter(branch=curBranch)
        for files in projectFiles:
            file_path = "" + str(files.project.file_path) + "/" + str(files.branch.name) + "/" + str(files.name)
            file = {}
            file["id"] = files.id # fariza's change: pulling the file's ID from database
            file["name"] = files.name
            file["path"] = file_path
            file["is_locked"] = files.is_locked # fariza's change: pulling the file's lock status from database
            fileList.append(file)
        return Response({"files":fileList})
    
class CreateFiles(APIView):

    def post(self, request):
        name = request.data.get("name", "").strip()
        if not name:
            return Response({"success": False, "error": "File name is required"}, status=status.HTTP_400_BAD_REQUEST)

        project_id = request.session.get("curProj")
        branch_id = request.session.get("curCom")

        if not project_id or not branch_id:
            return Response({"success": False, "error": "No project or branch selected"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from project.models import Project
            from projectbranch.models import Branch
            project = Project.objects.get(id=project_id)
            branch = Branch.objects.get(id=branch_id)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_404_NOT_FOUND)

        if models.ProjectFile.objects.filter(project=project, branch=branch, name=name).exists():
            return Response({"success": False, "error": "A file with that name already exists"}, status=status.HTTP_400_BAD_REQUEST)

        file = models.ProjectFile(project=project, branch=branch, name=name)
        file.save()

        try:
            file_service.create_file(project.id, branch.name, name)
        except Exception as e:
            print(f"Warning: Could not create S3 file: {e}")

        return Response({"success": True, "id": file.id, "name": file.name})


class CreateFolder(APIView):

    def post(self, request):
        name = request.data.get("name", "").strip()
        if not name:
            return Response({"success": False, "error": "Folder name is required"}, status=status.HTTP_400_BAD_REQUEST)

        project_id = request.session.get("curProj")
        branch_id = request.session.get("curCom")

        if not project_id or not branch_id:
            return Response({"success": False, "error": "No project or branch selected"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from project.models import Project
            from projectbranch.models import Branch
            project = Project.objects.get(id=project_id)
            branch = Branch.objects.get(id=branch_id)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_404_NOT_FOUND)

        folder_entry_name = name + "/"
        if models.ProjectFile.objects.filter(project=project, branch=branch, name=folder_entry_name).exists():
            return Response({"success": False, "error": "A folder with that name already exists"}, status=status.HTTP_400_BAD_REQUEST)

        folder = models.ProjectFile(project=project, branch=branch, name=folder_entry_name)
        folder.save()

        try:
            file_service.create_file(project.id, branch.name, folder_entry_name, "")
        except Exception as e:
            print(f"Warning: Could not create S3 folder: {e}")

        return Response({"success": True, "id": folder.id, "name": name})


# ============================================
# File Lock / Password Views
# ============================================

# fariza's change: class to handle creating and removing passwords on a file
class ToggleFileLock(APIView):
    def post(self, request):
        file_id = request.data.get("file_id") # fariza's change: get the file ID from the frontend
        password = request.data.get("password") # fariza's change: get the password from the frontend
        action = request.data.get("action") # fariza's change: check if we are locking or unlocking
        
        try:
            file_obj = models.ProjectFile.objects.get(id=file_id) # fariza's change: find the exact file in database
        except models.ProjectFile.DoesNotExist:
            return Response({"success": False, "error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
            
        if action == "lock":
            if not password:
                return Response({"success": False, "error": "Password required to lock file"}, status=status.HTTP_400_BAD_REQUEST)
            file_obj.is_locked = True
            file_obj.password_hash = make_password(password)
            file_obj.save()
            return Response({"success": True, "message": "File locked successfully", "is_locked": True})
            
        elif action == "unlock":
            # Require the old password to unlock it permanently
            if not password or not check_password(password, file_obj.password_hash):
                return Response({"success": False, "error": "Incorrect password"}, status=status.HTTP_403_FORBIDDEN)
            file_obj.is_locked = False
            file_obj.password_hash = None
            file_obj.save()
            return Response({"success": True, "message": "File unlocked successfully", "is_locked": False})
            
        return Response({"success": False, "error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

# fariza's change: class to verify if the entered password matches the file's lock password
class VerifyFilePassword(APIView):
    def post(self, request):
        file_id = request.data.get("file_id") # fariza's change: get the file ID from the frontend
        password = request.data.get("password") # fariza's change: get the password from the frontend
        
        try:
            file_obj = models.ProjectFile.objects.get(id=file_id) # fariza's change: find the exact file in database
        except models.ProjectFile.DoesNotExist:
            return Response({"success": False, "error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
            
        if not file_obj.is_locked:
            return Response({"success": True, "message": "File is not locked"})
            
        if check_password(password, file_obj.password_hash):
            return Response({"success": True, "message": "Password correct"})
        else:
            return Response({"success": False, "error": "Incorrect password"}, status=status.HTTP_403_FORBIDDEN)

# fariza's change: class to read the actual text inside a file, but only if the password is correct
class ReadFileContent(APIView):
    def post(self, request):
        file_id = request.data.get("file_id") # fariza's change: get the file ID from the frontend
        password = request.data.get("password") # fariza's change: get the password for locked files
        
        try:
            file_obj = models.ProjectFile.objects.get(id=file_id) # fariza's change: find the file in database
        except models.ProjectFile.DoesNotExist:
            return Response({"success": False, "error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
            
        # fariza's change: if the file is locked, we must check the password first
        if file_obj.is_locked:
            if not password or not check_password(password, file_obj.password_hash):
                return Response({"success": False, "error": "This file is locked. Please enter the correct password."}, status=status.HTTP_403_FORBIDDEN)
        
        # Read file content from S3
        result = file_service.read_file(file_obj.project.id, file_obj.branch.name, file_obj.name)
        if result["success"]:
            content = result["content"]
        else:
            content = ""

        return Response({
            "success": True,
            "content": content,
            "name": file_obj.name
        })


# fariza's change: class to delete a file from database and disk
class DeleteFile(APIView):
    def post(self, request):
        file_id = request.data.get("file_id") # get the ID of the file to delete
        
        if not file_id:
            return Response({"success": False, "error": "file_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            file_obj = models.ProjectFile.objects.get(id=file_id) # find the file in database
        except models.ProjectFile.DoesNotExist:
            return Response({"success": False, "error": "File not found in database"}, status=status.HTTP_404_NOT_FOUND)
            
        project_id = file_obj.project.id
        branch_name = file_obj.branch.name
        filename = file_obj.name

        try:
            file_service.delete_file_in_project(project_id, branch_name, filename)

            # fariza's change: delete from database permanently
            file_obj.delete()
            
            return Response({"success": True, "message": "File deleted successfully!"})
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



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


# fariza's change: class to rename a file on disk and update its name in the database
class RenameFile(APIView):
    def post(self, request):
        file_id = request.data.get("file_id") # get original file ID
        new_name = request.data.get("new_name") # get the desired new name
        
        if not file_id or not new_name:
            return Response({"success": False, "error": "file_id and new_name are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            file_obj = models.ProjectFile.objects.get(id=file_id) # find original record
        except models.ProjectFile.DoesNotExist:
            return Response({"success": False, "error": "File not found in database"}, status=status.HTTP_404_NOT_FOUND)
            
        # calculate where the file is on the computer's disk
        base_path = f"{file_obj.project.file_path}/{file_obj.branch.name}"
        old_path = os.path.join(base_path, file_obj.name)
        new_path = os.path.join(base_path, new_name)
        
        try:
            # fariza's change: rename the actual file on the computer's disk if it exists
            if os.path.exists(old_path):
                # check if a file with the new name already exists to avoid overwriting
                if os.path.exists(new_path):
                    return Response({"success": False, "error": f"A file named '{new_name}' already exists in this folder."}, status=status.HTTP_400_BAD_REQUEST)
                os.rename(old_path, new_path)
            
            # update the name in original record and save to database
            file_obj.name = new_name
            file_obj.save()
            
            return Response({"success": True, "new_name": new_name, "message": "File renamed successfully!"})
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)