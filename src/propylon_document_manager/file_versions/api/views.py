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
from django.db.models import Max

from ..models import FileVersion
from .serializers import FileVersionSerializer


class FileVersionViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FileVersionSerializer
    queryset = FileVersion.objects.all()
    lookup_field = "id"

    @action(detail=False, methods=["post"], url_path="upload")
    def upload(self, request):
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response({"detail": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        file_name = uploaded_file.name
        base_name, ext = os.path.splitext(file_name)
        last_version = (
            FileVersion.objects.filter(file_name=file_name).aggregate(max_v=Max("version_number"))
        )["max_v"]
        version_number = 0 if last_version is None else last_version + 1

        storage_dir = Path(settings.FILES_ROOT)
        storage_dir.mkdir(parents=True, exist_ok=True)
        filename_with_version = f"{base_name}.{version_number}{ext}"
        storage_path = storage_dir / filename_with_version
        with open(storage_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        file_version = FileVersion.objects.create(file_name=file_name, version_number=version_number)
        serializer = self.get_serializer(file_version)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, id=None):
        file_version = self.get_object()
        base_name, ext = os.path.splitext(file_version.file_name)
        filename_with_version = f"{base_name}.{file_version.version_number}{ext}"
        file_path = Path(settings.FILES_ROOT) / filename_with_version
        if not file_path.exists():
            return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)
        return FileResponse(open(file_path, "rb"), as_attachment=True, filename=file_version.file_name)
