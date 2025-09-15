from pathlib import Path

import pytest

from propylon_document_manager.file_versions.models import FileVersion
from propylon_document_manager.utils import FileDownload


def test_init_requires_filepath():
    with pytest.raises(ValueError):
        FileDownload(filepath="")


def test_init_rejects_negative_version(tmp_path: Path):
    with pytest.raises(ValueError):
        FileDownload(filepath=str(tmp_path / "sample.txt"), version=-1)


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
def test_get_file_data_respects_requested_version(tmp_path: Path):
    file_path = tmp_path / "specific.txt"
    first = FileVersion.objects.create(
        file_name=str(file_path),
        version_number=0,
        digest_hex="a" * 64,
    )
    FileVersion.objects.create(
        file_name=str(file_path),
        version_number=1,
        digest_hex="b" * 64,
    )

    downloader = FileDownload(filepath=str(file_path), version=0)

    record = downloader.get_file_data()

    assert record["id"] == first.id
    assert record["version_number"] == 0
    assert record["digest_hex"] == "a" * 64


@pytest.mark.django_db
def test_get_file_data_raises_when_not_found(tmp_path: Path):
    file_path = tmp_path / "unknown.txt"
    downloader = FileDownload(filepath=str(file_path))

    with pytest.raises(FileVersion.DoesNotExist):
        downloader._get_file_data(filepath=str(file_path), version=0)


@pytest.mark.django_db
def test_download_returns_file(tmp_path: Path, settings):
    file_path = tmp_path / "nested" / "report.txt"
    storage_dir = tmp_path / "storage"
    digest_hex = "a" * 64

    settings.FILES_ROOT = storage_dir

    storage_dir.mkdir(parents=True)
    stored_file = storage_dir / digest_hex
    stored_file.write_text("example content")

    FileVersion.objects.create(
        file_name=str(file_path),
        version_number=0,
        digest_hex=digest_hex,
    )

    downloader = FileDownload(filepath=str(file_path), version=0)

    message = downloader.download()

    assert message == f"File {file_path} downloaded successfully"
    assert file_path.exists()
    assert file_path.read_text() == "example content"


@pytest.mark.django_db
def test_download_returns_message_when_missing(tmp_path: Path, settings):
    settings.FILES_ROOT = tmp_path / "storage"

    downloader = FileDownload(filepath=str(tmp_path / "missing.txt"))

    assert downloader.download() == "That file does not exist on the server"


@pytest.mark.django_db
def test_download_returns_message_when_digest_missing(tmp_path: Path, settings):
    file_path = tmp_path / "orphaned.txt"
    settings.FILES_ROOT = tmp_path / "storage"

    FileVersion.objects.create(
        file_name=str(file_path),
        version_number=0,
        digest_hex=None,
    )

    downloader = FileDownload(filepath=str(file_path), version=0)

    assert downloader.download() == "That file does not exist on the server"


@pytest.mark.django_db
def test_download_returns_message_when_source_missing(tmp_path: Path, settings):
    file_path = tmp_path / "report.txt"
    settings.FILES_ROOT = tmp_path / "storage"

    FileVersion.objects.create(
        file_name=str(file_path),
        version_number=0,
        digest_hex="b" * 64,
    )

    downloader = FileDownload(filepath=str(file_path), version=0)

    assert downloader.download() == "That file does not exist on the server"


@pytest.mark.django_db
def test_download_returns_error_when_copy_fails(
    tmp_path: Path, settings, monkeypatch
):
    file_path = tmp_path / "error.txt"
    storage_dir = tmp_path / "storage"
    digest_hex = "d" * 64

    settings.FILES_ROOT = storage_dir

    storage_dir.mkdir(parents=True)
    stored_file = storage_dir / digest_hex
    stored_file.write_text("content")

    FileVersion.objects.create(
        file_name=str(file_path),
        version_number=0,
        digest_hex=digest_hex,
    )

    downloader = FileDownload(filepath=str(file_path), version=0)

    def raise_oserror(*args, **kwargs):
        raise OSError("permission denied")

    monkeypatch.setattr(
        "propylon_document_manager.utils.file_download.shutil.copy2",
        raise_oserror,
    )

    message = downloader.download()

    assert message == f"Error downloading {file_path}: permission denied"
