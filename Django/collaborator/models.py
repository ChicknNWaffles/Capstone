from django.db import models
from django.contrib.auth.models import User
from project.models import Project

# Create your models here.
class Collaborator(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    #pk = models.CompositePrimaryKey("user_id", "project_id")

    admin_perms = models.BooleanField(default=False)
    edit_perms = models.BooleanField(default=False)
    hours = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} on {self.project.name}"