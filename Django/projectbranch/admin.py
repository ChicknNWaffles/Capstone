from django.contrib import admin
from . import models

# Register your models here.

class projectBranchAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'name', 'isMain')
    list_filter = ('id', 'project', 'name')
    search_fields = ('id', 'project', 'name')

admin.site.register(models.Branch, projectBranchAdmin)
