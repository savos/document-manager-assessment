import hashlib
from pathlib import Path

import pytest

from propylon_document_manager.file_versions.models import FileVersion
from propylon_document_manager.utils import FileUpload


def create_temp_file(tmp_path: Path, filename: str, content: str = "test content") -> Path:
    file_path = tmp_path / filename
    file_path.write_text(content)
    return file_path


def test_file_upload_requires_filepath():
    with pytest.raises(ValueError, match="A file path must be provided."):
        FileUpload("")



def test_file_upload_raises_file_not_found(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        FileUpload(tmp_path / "missing.txt")



def test_file_upload_requires_actual_file(tmp_path: Path):
    directory_path = tmp_path / "subdir"
    directory_path.mkdir()

    with pytest.raises(ValueError, match="does not point to a file"):
        FileUpload(directory_path)


@pytest.mark.django_db
def test_get_latest_version_without_existing_records(tmp_path: Path):
    file_path = create_temp_file(tmp_path, "first.txt")
    uploader = FileUpload(file_path)

    assert uploader.get_latest_version() == 0


@pytest.mark.django_db
def test_get_latest_version_with_existing_records(tmp_path: Path):
    file_path = create_temp_file(tmp_path, "history.txt")

    FileVersion.objects.create(file_name=str(file_path), version_number=0)
    FileVersion.objects.create(file_name=str(file_path), version_number=1)

    uploader = FileUpload(file_path)

    assert uploader.get_latest_version() == 2


@pytest.mark.django_db
def test_upload_detects_duplicate_digest(tmp_path: Path, settings):
    file_path = create_temp_file(tmp_path, "duplicate.txt", "duplicate data")
    digest = hashlib.sha256(b"duplicate data").hexdigest()

    FileVersion.objects.create(
        file_name="other.txt",
        version_number=0,
        digest_hex=digest,
    )

    settings.FILES_ROOT = tmp_path / "storage"
    uploader = FileUpload(file_path)

    assert uploader.upload() == "File already exists."
    assert not FileVersion.objects.filter(file_name=str(file_path)).exists()


@pytest.mark.django_db
def test_upload_detects_existing_file_on_disk(tmp_path: Path, settings):
    file_path = create_temp_file(tmp_path, "on_disk.txt", "data on disk")
    settings.FILES_ROOT = tmp_path / "storage"

    uploader = FileUpload(file_path)
    destination_path = Path(settings.FILES_ROOT) / uploader.digest_hex
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    destination_path.write_text("existing")

    assert uploader.upload() == "File already exists."
    assert FileVersion.objects.filter(file_name=str(file_path)).count() == 0


@pytest.mark.django_db
def test_upload_saves_file_and_creates_record(tmp_path: Path, settings):
    file_path = create_temp_file(tmp_path, "fresh.txt", "fresh data")
    settings.FILES_ROOT = tmp_path / "storage"

    uploader = FileUpload(file_path)
    message = uploader.upload()

    expected_path = Path(settings.FILES_ROOT) / uploader.digest_hex

    assert message == f"File {file_path} saved successfully"
    assert expected_path.exists()

    record = FileVersion.objects.get(file_name=str(file_path))
    assert record.version_number == 0
    assert record.digest_hex == uploader.digest_hex


@pytest.mark.django_db
def test_upload_assigns_incremented_version(tmp_path: Path, settings):
    file_path = create_temp_file(tmp_path, "versioned.txt", "updated content")
    settings.FILES_ROOT = tmp_path / "storage"

    FileVersion.objects.create(
        file_name=str(file_path),
        version_number=0,
        digest_hex="a" * 64,
    )
    FileVersion.objects.create(
        file_name=str(file_path),
        version_number=1,
        digest_hex="b" * 64,
    )

    uploader = FileUpload(file_path)
    message = uploader.upload()

    assert message == f"File {file_path} saved successfully"

    record = FileVersion.objects.get(file_name=str(file_path), digest_hex=uploader.digest_hex)
    assert record.version_number == 2


@pytest.mark.django_db
def test_upload_handles_copy_error(tmp_path: Path, settings, monkeypatch):
    file_path = create_temp_file(tmp_path, "error.txt", "will fail")
    settings.FILES_ROOT = tmp_path / "storage"

    uploader = FileUpload(file_path)

    def raise_os_error(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr("propylon_document_manager.utils.file_upload.shutil.copy2", raise_os_error)

    message = uploader.upload()
    expected_path = Path(settings.FILES_ROOT) / uploader.digest_hex

    assert message == f"Error saving {file_path}: disk full"
    assert not expected_path.exists()
    assert not FileVersion.objects.filter(file_name=str(file_path)).exists()
