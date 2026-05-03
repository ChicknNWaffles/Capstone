from django.db import models
from project.models import Project
from projectbranch.models import Branch


# Create your models here.
class ProjectFile(models.Model):

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    name = models.CharField(max_length=255, default="")
    file_path = models.CharField(max_length=255, default="")

    # fariza's change: added field to track if the file is locked with a password
    is_locked = models.BooleanField(default=False)
    # fariza's change: added field to store the secured password string
    password_hash = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return self.name