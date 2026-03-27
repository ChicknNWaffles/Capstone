from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from project.models import Project
from projectbranch.models import Branch



@api_view(["GET", "POST"])
def projects(request):
    if request.method == "GET":
        data = Project.objects.all().values()
        return Response(list(data))

    # POST
    name = request.data.get("name")
    if not name:
        return Response({"error": "name is required"}, status=status.HTTP_400_BAD_REQUEST)

    project = Project.objects.create(
        name=name,
        description=request.data.get("description", "")
    )
    return Response({"id": project.id, "name": project.name}, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(["POST"])
@authentication_classes([])
@permission_classes([permissions.AllowAny])
# for log in page
def login_api(request):
    username = (request.data.get("username") or "").strip()
    password = (request.data.get("password") or "").strip()

    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response({"error": "invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    login(request, user)
    return Response({"ok": True, "username": user.username})

# for sign up page
@csrf_exempt
@api_view(["POST"])
@authentication_classes([])
@permission_classes([permissions.AllowAny])
def signup_api(request):
    username = (request.data.get("username") or "").strip()
    email = (request.data.get("email") or "").strip()
    password = (request.data.get("password") or "").strip()

    if not username or not password:
        return Response({"error": "username and password required"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "username already exists"}, status=status.HTTP_409_CONFLICT)

    if email and User.objects.filter(email=email).exists():
        return Response({"error": "email already exists"}, status=status.HTTP_409_CONFLICT)

    user = User.objects.create_user(username=username, email=email, password=password)
    login(request, user)  # auto-login after signup
    return Response({"ok": True, "username": user.username}, status=status.HTTP_201_CREATED)

# checks the session as a "who am i"
@api_view(["GET"])
def me(request):
    if request.user.is_authenticated:
        return Response({"authenticated": True, "username": request.user.username})
    return Response({"authenticated": False}, status=status.HTTP_401_UNAUTHORIZED)

# fariza's change: gets the name and details of the current project
@api_view(["GET"])
def getProjName(request):
    # get the project that the current user is looking at from a session variable
    proj_id = request.session.get("curProj")
    if not proj_id:
        return Response({"name": "unknownProject", "visibility": False, "repo_link": ""})
    
    try:
        project = Project.objects.get(id=proj_id)
        return Response({
            "name": project.name,
            "visibility": project.visibility,
            "repo_link": project.repo_link
        })
    except Project.DoesNotExist:
        return Response({"name": "unknownProject", "visibility": False, "repo_link": ""})

# gets the name of the current commit
@api_view(["GET"])
def getComName(request):
    # get the project that the current user is looking at from a session variable
    comName = request.session.get("curComName", "unknownCommit")
    # send to front end
    return Response({"name":comName})

# sets the current project
@api_view(["POST"])
def setCurProj(request):
    project = Project.objects.get(id = request.data.get("project"))
    request.session["curProj"] = project.id
    request.session["curProjName"] = project.name
    return Response({"ok":True})

# sets the current branch
@api_view(["POST"])
def setCurBranch(request):
    proj = request.session.get("curProj")
    main = Branch.objects.filter(project__id=proj).filter(isMain=True).first()
    if main is None:
        from project.models import Project
        main = Branch.objects.create(project_id=proj, name="main", isMain=True)
    print(main)
    branch = Branch.objects.get(id = request.data.get("com") or main.id)
    request. session["curCom"] = branch.id
    request.session["curComName"] = branch.name
    return Response({"ok":True})

# fariza's change: updates project general settings (visibility and repo link)
@csrf_exempt
@api_view(["POST"])
def updateProjectSettings(request):
    proj_id = request.session.get("curProj")
    if not proj_id:
        return Response({"success": False, "error": "No project selected in session"}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        project = Project.objects.get(id=proj_id)
        
        # Update name
        new_name = request.data.get("name")
        if new_name:
            project.name = new_name
            request.session["curProjName"] = new_name # sync session
            
        # Update visibility (front-end sends "Private Workspace" or "Public Collaborative")
        visibility_val = request.data.get("visibility")
        if visibility_val is not None:
            # If it's a string from the select box:
            if isinstance(visibility_val, str):
                project.visibility = (visibility_val == "Public Collaborative")
            else:
                project.visibility = bool(visibility_val)
                
        # Update repo link
        repo_link = request.data.get("repo_link")
        if repo_link is not None:
            project.repo_link = repo_link
            
        project.save()
        return Response({
            "success": True, 
            "message": "Settings updated",
            "visibility": project.visibility,
            "repo_link": project.repo_link
        })
    except Project.DoesNotExist:
        return Response({"success": False, "error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
