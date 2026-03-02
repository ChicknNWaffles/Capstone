from rest_framework import serializers
from django.contrib.auth.models import User

class CollaboratorSerializer(serializers.Serializer):

    admin_perms = serializers.BooleanField()
    edit_perms = serializers.BooleanField()
    hours = serializers.IntegerField()

    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True)