from django.db import models
from project.models import Project

# Create your models here.
class Branch(models.Model):
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default="")
    isMain = models.BooleanField(default=False)
    filepath = models.CharField(max_length=255, default="")


    def __str__(self):
        return self.name