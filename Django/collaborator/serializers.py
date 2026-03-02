from rest_framework import serializers

class CollaboratorSerializer(serializers.Serializer):

    admin_perms = serializers.BooleanField()
    edit_perms = serializers.BooleanField()
    hours = serializers.IntegerField()
