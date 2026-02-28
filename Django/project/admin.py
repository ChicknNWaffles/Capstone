from django.contrib import admin
from . import models

# Register your models here.
# admin.site.register(models.Project)

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'file_path', 'visibility')
    list_filter = ('name',)
    search_fields = ('name', 'visibility')

admin.site.register(models.Project, ProjectAdmin)