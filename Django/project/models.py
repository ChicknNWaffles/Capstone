from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Project(models.Model):

    name = models.CharField(max_length=255, default="")
    file_path = models.CharField(max_length=255, default="")
    visibility = models.BooleanField(default=False)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    repo_link = models.CharField(max_length=255, default="")
    last_edited = models.DateField(auto_now=True)

    def __str__(self):
        return self.name