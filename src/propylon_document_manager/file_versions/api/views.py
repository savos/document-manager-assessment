import os
from pathlib import Path

from django.conf import settings
from django.http import FileResponse

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..models import FileVersion
from .serializers import FileVersionSerializer


class FileVersionViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FileVersionSerializer
    queryset = FileVersion.objects.all()
    lookup_field = "id"

    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, id=None):
        file_version = self.get_object()
        base_name, ext = os.path.splitext(file_version.file_name)
        filename_with_version = f"{base_name}.{file_version.version_number}{ext}"
        file_path = Path(settings.FILES_ROOT) / filename_with_version
        if not file_path.exists():
            return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)
        return FileResponse(open(file_path, "rb"), as_attachment=True, filename=file_version.file_name)
