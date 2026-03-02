from django.db import models
from project.models import Project
from projectbrach.models import Branch


# Create your models here.
class ProjectFile(models.Model):

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    name = models.CharField(max_length=255, default="")
    # file_path = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.name