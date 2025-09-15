import hashlib

import pytest
from rest_framework.test import APIClient

from propylon_document_manager.file_versions.models import FileVersion, UserFileVersion
from propylon_document_manager.utils import FileUpload
from .factories import UserFactory

def test_file_versions():
    file_name = "new_file"
    file_version = 1
    digest_hex = "0" * 64
    FileVersion.objects.create(
        file_name=file_name,
        version_number=file_version,
        digest_hex=digest_hex,
    )
    files = FileVersion.objects.all()
    assert files.count() == 1
    assert files[0].file_name == file_name
    assert files[0].version_number == file_version
    assert files[0].digest_hex == digest_hex


def test_user_fileversion():
    user = UserFactory()
    file_version = FileVersion.objects.create(
        file_name="another_file",
        version_number=0,
    )
    mapping = UserFileVersion.objects.create(fileversion=file_version, user=user)
    assert mapping.fileversion == file_version
    assert mapping.user == user
    assert mapping.fileversion.digest_hex is None


def test_file_upload_computes_digest(tmp_path):
    file_path = tmp_path / "example.txt"
    file_path.write_text("sample content")

    uploader = FileUpload(file_path)

    expected_digest = hashlib.sha256(b"sample content").hexdigest()
    assert uploader.digest_hex == expected_digest


@pytest.mark.django_db
def test_file_upload_view_returns_digest(user, tmp_path):
    file_path = tmp_path / "upload.txt"
    file_path.write_text("data for digest")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/file-uploads/",
        {"filepath": str(file_path)},
        format="json",
    )

    assert response.status_code == 200
    assert response.json()["digest_hex"] == hashlib.sha256(b"data for digest").hexdigest()


@pytest.mark.django_db
def test_file_upload_view_handles_missing_file(user):
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/file-uploads/",
        {"filepath": "/tmp/non-existent-file"},
        format="json",
    )

    assert response.status_code == 404
    assert "detail" in response.json()
