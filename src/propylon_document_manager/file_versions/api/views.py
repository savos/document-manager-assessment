import os
from pathlib import Path

from django.conf import settings
from django.http import FileResponse
from django.utils.encoding import smart_str
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django.db.models import Max

from ..models import FileVersion
from .serializers import FileVersionSerializer


@method_decorator(csrf_exempt, name="dispatch")
class FileVersionViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FileVersionSerializer
    queryset = FileVersion.objects.all()
    lookup_field = "id"

    def _safe_join(self, directory: str) -> Path:
        base = Path(settings.FILES_ROOT).resolve()
        target = (base / directory).resolve()
        if not str(target).startswith(str(base)):
            raise ValueError("Invalid directory path")
        return target

    @action(detail=False, methods=["post"], url_path="upload")
    def upload(self, request):
        uploaded_file = request.FILES.get("file")
        directory = request.data.get("directory", "")
        if not uploaded_file:
            return Response({"detail": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        file_name = uploaded_file.name
        base_name, ext = os.path.splitext(file_name)
        last_version = (
            FileVersion.objects.filter(file_name=file_name).aggregate(max_v=Max("version_number"))
        )["max_v"]
        version_number = 0 if last_version is None else last_version + 1

        safe_dir = self._safe_join(directory)
        safe_dir.mkdir(parents=True, exist_ok=True)
        filename_with_version = f"{base_name}.{version_number}{ext}"
        storage_path = safe_dir / filename_with_version
        with open(storage_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        relative_path = str(Path(directory) / filename_with_version) if directory else filename_with_version
        file_version = FileVersion.objects.create(
            path=relative_path, file_name=file_name, version_number=version_number
        )
        serializer = self.get_serializer(file_version)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, id=None):
        file_version = self.get_object()
        file_path = Path(settings.FILES_ROOT) / smart_str(file_version.path or "")
        if not file_path.exists():
            return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)
        return FileResponse(open(file_path, "rb"), as_attachment=True, filename=file_version.file_name)

    @action(detail=False, methods=["post"], url_path="directories")
    def create_directory(self, request):
        directory = request.data.get("parent", "")
        name = request.data.get("name")
        if not name:
            return Response({"detail": "Name is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            target_dir = self._safe_join(Path(directory) / name)
            target_dir.mkdir(parents=True, exist_ok=False)
        except Exception:
            return Response(
                {"detail": "Cannot create a directory with that name."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"path": str(Path(directory) / name)}, status=status.HTTP_201_CREATED)
