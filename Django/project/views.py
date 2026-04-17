from django.shortcuts import render # render is for templates
from django.views import View
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView, Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from collaborator.views import unique_color_per_project
from project.models import Project
from project.serializers import ProjectSerializer

from collaborator.models import Collaborator
from collaborator.serializers import CollaboratorSerializer

from projectbranch.models import Branch
from projectbranch.serializers import ProjectBranchSerializer

from api.file_service import file_service


# Create your views here.
class getProjects(View):
    
    def get(self, request):

        # this one is getProjects(APIView)
        # projects = models.Project.objects.all().values()
        # response = Response(projects)

        # this one is getProjects(View)
        html = ""
        user = request.user
        projects = Project.objects.filter(owner=user)
        # Project.objects.filter()
        # Project.objects.get()
        # Project.objects.filter(id__lt = 7)
        for project in projects:
            html += f"<h1>Name: {project.name}</h1>"
            html += f"<p>ID: {project.id}</p>"
            if project.visibility:
                html += f"<p>Public</p>"
            else: 
                html += "<p>Private<p>"
            html += f"<p>Filepath: {project.file_path}</p>"
            html += f"<p>Repo link: {project.repo_link}</p>"
            html += f"<p>{project.last_edited}</p>"
        response = HttpResponse(html)

        # if doing templates use:
        # response = render()
        return response
    
class getUserProjects(APIView):
    def get(self,request):
        user = request.user
        from collaborator.models import Collaborator
        collab_project_ids = Collaborator.objects.filter(user=user).values_list('project_id', flat=True)
        from django.db.models import Q
        projects = Project.objects.filter(Q(owner=user) | Q(id__in=collab_project_ids))
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
        visibility = request.data.get("visibility") == "public"
        repoLink = request.data.get("repoLink") or ""


        # example of a guard
        # check for name
        if name is None:
            response = {
                "success": False,
                "message": "User must provide project name"
            }
            return Response(response, status=status.HTTP_204_NO_CONTENT)

        # check for visibility
        if visibility is None:
            response = {
                "success": False,
                "message": "User must provide info about visibility"
            }
            return Response(response, status=status.HTTP_204_NO_CONTENT)
        
        project = Project(
            name=name,
            visibility=visibility,
            file_path="",
            owner=user,
            repo_link=repoLink,
        )
        project.save()

        # Set S3 path and create the folder in the bucket
        project.file_path = f"projects/{project.id}/"
        project.save()
        # fariza's change: wrapped S3 call in try/except so it doesn't crash when running locally without AWS
        try:
            file_service.create_project_folder(project.id)
        except Exception as e:
            # S3 is not set up locally — skip this step, project is still saved
            print(f"Warning: Could not create S3 folder (skipping): {e}")

        # Auto-create main branch
        from projectbranch.models import Branch
        Branch.objects.create(project=project, name="main", isMain=True)

        response = {
            "success": True,
            "id": project.id,
            "name": project.name,
            "filepath": project.file_path,
            "visibility": project.visibility,
            "repoLink":project.repo_link,
            "last_edited":project.last_edited,

        }

        return Response(response)
    
class CreateProjectButWithSerializers(APIView):

    serializer_class = ProjectSerializer
    
    def post(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid()
        data = serializer.validated_data

        project = Project(
            name=data.get("name"),
            visibility=data.get("visibility"),
            file_path=data.get("file_path"),
            owner=user,
            repo_link=data.get("repo_link"),
        )
        project.save()

        main_branch = Branch(
            project=project,
            name="main",
        )
        main_branch.save()

        response = {
            "success": True,
            "name": project.name,
            "filepath": project.file_path,
            "visibility": project.visibility,
            "repoLink":project.repo_link,
            "last_edited":project.last_edited,

        }

        return Response(response)

# fariza's change: added delete project feature — only the owner can delete their own project
class DeleteProject(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        # only allow the owner to delete, not other users
        if project.owner != request.user:
            return Response({"error": "You do not have permission to delete this project."}, status=status.HTTP_403_FORBIDDEN)
        project.delete()
        return Response({"success": True}, status=status.HTTP_200_OK)


    def get(self, request):
        pass

class ProjectCollaboratorsListCreate(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CollaboratorSerializer

    def get(self, request, project_id):
        collaborators = Collaborator.objects.filter(project_id=project_id)
        serializer = self.serializer_class(collaborators, many=True)
        
        return Response({
            "collaborators": serializer.data,
            "project_id": project_id,
        })

    def post(self, request, project_id):
        user = request.user
        
        # Get the project from URL
        project = get_object_or_404(Project, id=project_id)
        
        # Permission check
        if project.owner != user:
            return Response(
                {"detail": "Only the project owner can add collaborators."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data

        # Create the collaborator 
        collaborator = Collaborator(
            project=project,
            user=data.get('user'),
            admin_perms=data.get('admin_perms', False),
            edit_perms=data.get('edit_perms', False),
            hours=data.get('hours', 0),
            color=unique_color_per_project(project, data.get('user')),
        )
        collaborator.save()

        # Success response
        response = {
            "success": True,
            "user": collaborator.user.username,
            "project": project.name,
            "admin_perms": collaborator.admin_perms,
            "edit_perms": collaborator.edit_perms,
            "hours": collaborator.hours,
            "color": collaborator.color,
        }

        return Response(response)
    
    
class ProjectBranches(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectBranchSerializer

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)

        # Perms check
        is_owner = project.owner == request.user
        is_collaborator = Collaborator.objects.filter(
            project=project,
            user=request.user
        ).exists()

        if not (is_owner or is_collaborator):
            return Response(
                {"detail": "Only the project owner or collaborators can create branches."},
                status=status.HTTP_403_FORBIDDEN
            )

        # serialize data
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data

        branch = Branch(
            project=project,
            name=data.get("name"),
        )
        branch.save()
        
        response = {
            "success": True,
            "name": branch.name,
            "project": project.name,
        }
        return Response(response, status=status.HTTP_201_CREATED)
