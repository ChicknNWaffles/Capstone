from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Collaborator

class CollaboratorSerializer(serializers.Serializer):

    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )

    admin_perms = serializers.BooleanField()
    edit_perms = serializers.BooleanField()
    hours = serializers.IntegerField()
