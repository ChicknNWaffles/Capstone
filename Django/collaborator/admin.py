from django.contrib import admin
from . import models

# Register your models here.

class CollaboratorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project', 'admin_perms', 'edit_perms', 'hours')
    list_filter = ('id', 'user', 'project', 'admin_perms', 'edit_perms', 'hours')
    search_fields = ('id', 'user', 'project', 'admin_perms', 'edit_perms', 'hours')

admin.site.register(models.Collaborator, CollaboratorAdmin)