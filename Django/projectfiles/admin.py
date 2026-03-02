from django.contrib import admin
from . import models

# Register your models here.

class ProjectFilesAdmin(admin.ModelAdmin):
    list_display = ('branch', 'project', 'name')
    list_filter = ('name', 'branch', 'project')
    search_fields = ('name', 'branch', 'project')

admin.site.register(models.ProjectFile, ProjectFilesAdmin)