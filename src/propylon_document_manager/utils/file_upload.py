"""Utilities for handling file uploads."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Union


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


__all__ = ["FileUpload"]
