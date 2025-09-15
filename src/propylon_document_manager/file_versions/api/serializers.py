from rest_framework import serializers

from ..models import FileVersion, UserFileVersion

class FileVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileVersion
        fields = "__all__"


class UserFileVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFileVersion
        fields = "__all__"
