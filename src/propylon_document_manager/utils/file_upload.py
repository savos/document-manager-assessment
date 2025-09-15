"""Utilities for handling file uploads."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from typing import Union

from django.conf import settings
from django.db.models import Max


class FileUpload:
    """Read a file and calculate its SHA-256 digest."""

    def __init__(self, filepath: Union[str, Path]):
        if not filepath:
            raise ValueError("A file path must be provided.")

        self.filepath = Path(filepath)
        if not self.filepath.exists():
            raise FileNotFoundError(f"File not found: {self.filepath}")
        if not self.filepath.is_file():
            raise ValueError(f"The path does not point to a file: {self.filepath}")

        self.digest_hex = self._calculate_digest()

    def _calculate_digest(self) -> str:
        hasher = hashlib.sha256()
        with self.filepath.open("rb") as file_obj:
            for chunk in iter(lambda: file_obj.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def check_duplicate(self) -> bool:
        """Check whether a file with the same digest already exists."""

        from propylon_document_manager.file_versions.models import FileVersion

        if not self.digest_hex:
            return False

        return FileVersion.objects.filter(digest_hex=self.digest_hex).exists()

    def get_latest_version(self) -> int:
        """Return the next version number for the current file."""

        from propylon_document_manager.file_versions.models import FileVersion

        latest_version = (
            FileVersion.objects.filter(file_name=str(self.filepath))
            .aggregate(max_version=Max("version_number"))
            .get("max_version")
        )

        if latest_version is None:
            return 0

        return latest_version + 1

    def upload(self) -> str:
        """Store the uploaded file and create its database record."""

        from propylon_document_manager.file_versions.models import FileVersion

        if self.check_duplicate():
            return "File already exists."

        storage_directory = Path(settings.FILES_ROOT)
        destination_path = storage_directory / self.digest_hex

        if destination_path.exists():
            return "File already exists."

        try:
            storage_directory.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.filepath, destination_path)
        except OSError as exc:
            return f"Error saving {self.filepath}: {exc}"

        version_number = self.get_latest_version()
        FileVersion.objects.create(
            file_name=str(self.filepath),
            version_number=version_number,
            digest_hex=self.digest_hex,
        )

        return f"File {self.filepath} saved successfully"


__all__ = ["FileUpload"]
