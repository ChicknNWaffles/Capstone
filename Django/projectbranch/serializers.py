from rest_framework import serializers

class ProjectBranchSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=255)
    # isMain = serializers.BooleanField()

