"""Utilities for retrieving stored file version details."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Optional, Union

from django.db.models import Max


class FileDownload:
    """Fetch metadata for stored file versions."""

    def __init__(self, filepath: Union[str, Path], version: Optional[int] = None):
        if not filepath:
            raise ValueError("A file path must be provided.")

        self.filepath = str(filepath)
        if version is not None:
            if version < 0:
                raise ValueError("Version must be a non-negative integer.")
            self.version = int(version)
        else:
            self.version = None
    def _get_max_version(self, filepath: Optional[Union[str, Path]] = None) -> int:
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
            self._get_max_version(target_path)
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


__all__ = ["FileDownload"]
