from rest_framework import serializers

class ProjectSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=255)

