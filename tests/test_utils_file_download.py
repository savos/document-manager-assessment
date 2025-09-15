from pathlib import Path

import pytest

from propylon_document_manager.file_versions.models import FileVersion
from propylon_document_manager.utils import FileDownload


@pytest.mark.django_db
def test_get_max_version_returns_highest_value(tmp_path: Path):
    file_path = tmp_path / "example.txt"
    FileVersion.objects.create(file_name=str(file_path), version_number=0)
    FileVersion.objects.create(file_name=str(file_path), version_number=3)

    downloader = FileDownload(filepath=str(file_path))

    assert downloader._get_max_version() == 3


@pytest.mark.django_db
def test_get_max_version_raises_when_missing(tmp_path: Path):
    downloader = FileDownload(filepath=str(tmp_path / "missing.txt"))

    with pytest.raises(FileVersion.DoesNotExist):
        downloader._get_max_version()


@pytest.mark.django_db
def test_get_file_data_defaults_to_latest_version(tmp_path: Path):
    file_path = tmp_path / "history.txt"
    FileVersion.objects.create(file_name=str(file_path), version_number=0)
    latest = FileVersion.objects.create(
        file_name=str(file_path),
        version_number=1,
        digest_hex="b" * 64,
    )

    downloader = FileDownload(filepath=str(file_path))

    record = downloader._get_file_data(filepath=str(file_path), version=None)

    assert record["id"] == latest.id
    assert record["version_number"] == 1


@pytest.mark.django_db
def test_get_file_data_raises_when_not_found(tmp_path: Path):
    file_path = tmp_path / "unknown.txt"
    downloader = FileDownload(filepath=str(file_path))

    with pytest.raises(FileVersion.DoesNotExist):
        downloader._get_file_data(filepath=str(file_path), version=0)
