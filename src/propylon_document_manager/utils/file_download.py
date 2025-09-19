"""Utilities for retrieving stored file version details."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Any, Mapping, Optional, Union

from django.conf import settings
from django.db.models import Max

if TYPE_CHECKING:
    from propylon_document_manager.file_versions.models import User


class FileDownload:
    """Fetch metadata for stored file versions."""

    def __init__(
        self,
        filepath: Union[str, Path],
        version: Optional[int] = None,
        user: Optional["User"] = None,
    ):
        if not filepath:
            raise ValueError("A file path must be provided.")

        self.filepath = str(filepath)
        if version is not None:
            if version < 0:
                raise ValueError("Version must be a non-negative integer.")
            self.version = int(version)
        else:
            self.version = None
        self.user = user

    def get_files_of_user(self, user: Optional["User"] = None) -> list[int]:
        """Return IDs of file versions owned by the provided or configured user."""

        from propylon_document_manager.file_versions.models import UserFileVersion

        target_user = user if user is not None else self.user
        if target_user is None or not getattr(target_user, "is_authenticated", False):
            return []

        if getattr(target_user, "pk", None) is None:
            return []

        return list(
            UserFileVersion.objects.filter(user=target_user)
            .values_list("fileversion_id", flat=True)
            .distinct()
        )

    def file_list(self, user: Optional["User"] = None) -> list[dict[str, Any]]:
        """Return metadata for all file versions available to the current user."""

        from propylon_document_manager.file_versions.models import FileVersion

        file_version_ids = self.get_files_of_user(user=user)
        if not file_version_ids:
            return []

        records = (
            FileVersion.objects.filter(id__in=file_version_ids)
            .values("file_name", "version_number")
            .order_by("file_name", "version_number")
        )

        return [
            {"file_name": record["file_name"], "version": record["version_number"]}
            for record in records
        ]

    def get_file_data(self) -> Mapping[str, Any]:
        """Return metadata for the configured file path and version."""

        return self._get_file_data(filepath=self.filepath, version=self.version)

    def _get_latest_version(self, filepath: Optional[Union[str, Path]] = None) -> int:
        """Return the latest stored version number for the file."""

        from propylon_document_manager.file_versions.models import FileVersion

        target_path = self.filepath if filepath is None else str(filepath)
        result = (
            FileVersion.objects.filter(file_name=target_path)
            .aggregate(max_version=Max("version_number"))
            .get("max_version")
        )

        if result is None:
            raise FileVersion.DoesNotExist(
                f"No versions found for file: {target_path}"
            )

        return int(result)

    def _get_file_data(
        self, filepath: Union[str, Path], version: Optional[int]
    ) -> Mapping[str, Any]:
        """Return the database row for the requested file version."""

        from propylon_document_manager.file_versions.models import FileVersion

        target_path = str(filepath)
        resolved_version = (
            self._get_latest_version(target_path)
            if version is None
            else int(version)
        )

        try:
            return FileVersion.objects.values().get(
                file_name=target_path, version_number=resolved_version
            )
        except FileVersion.DoesNotExist as exc:
            raise FileVersion.DoesNotExist(
                f"No file version found for {target_path} with version {resolved_version}."
            ) from exc

    def download(self) -> str:
        """Retrieve the stored file and save it to the configured path."""

        from propylon_document_manager.file_versions.models import FileVersion

        try:
            file_data = self.get_file_data()
        except FileVersion.DoesNotExist:
            return "That file does not exist on the server"

        if not file_data:
            return "That file does not exist on the server"

        digest_hex = file_data.get("digest_hex")
        if not digest_hex:
            return "That file does not exist on the server"

        storage_directory = Path(settings.FILES_ROOT)
        source_path = storage_directory / digest_hex

        if not source_path.exists() or not source_path.is_file():
            return "That file does not exist on the server"

        destination_path = Path(self.filepath)
        destination_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            shutil.copy2(source_path, destination_path)
        except OSError as exc:
            return f"Error downloading {destination_path}: {exc}"

        return f"File {destination_path} downloaded successfully"


__all__ = ["FileDownload"]
