from rest_framework import serializers

class ProjectSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=255)
    file_path = serializers.CharField(max_length=255, read_only=True)
    visibility = serializers.BooleanField()
    repo_link = serializers.CharField(max_length=255)
