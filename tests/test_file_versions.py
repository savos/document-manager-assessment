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


@pytest.mark.django_db
def test_file_upload_duplicate_detection(tmp_path):
    file_path = tmp_path / "duplicate.txt"
    file_contents = "duplicate content"
    file_path.write_text(file_contents)

    FileVersion.objects.create(
        file_name="existing.txt",
        version_number=1,
        digest_hex=hashlib.sha256(file_contents.encode()).hexdigest(),
    )

    uploader = FileUpload(file_path)

    assert uploader.check_duplicate() is True


@pytest.mark.django_db
def test_file_upload_duplicate_detection_returns_false(tmp_path):
    file_path = tmp_path / "unique.txt"
    file_path.write_text("unique content")

    FileVersion.objects.create(
        file_name="different.txt",
        version_number=1,
        digest_hex="0" * 64,
    )

    uploader = FileUpload(file_path)

    assert uploader.check_duplicate() is False


@pytest.mark.django_db
def test_file_list_endpoint_returns_all_files(user):
    first = FileVersion.objects.create(
        file_name="alpha.txt",
        version_number=0,
        digest_hex="a" * 64,
    )
    second = FileVersion.objects.create(
        file_name="beta.txt",
        version_number=1,
        digest_hex="b" * 64,
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/files/")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": first.id,
            "file_name": "alpha.txt",
            "version_number": 0,
            "digest_hex": "a" * 64,
        },
        {
            "id": second.id,
            "file_name": "beta.txt",
            "version_number": 1,
            "digest_hex": "b" * 64,
        },
    ]


@pytest.mark.django_db
def test_user_file_list_endpoint_returns_files_for_authenticated_user(user, user_factory):
    first = FileVersion.objects.create(file_name="alpha.txt", version_number=0)
    second = FileVersion.objects.create(file_name="beta.txt", version_number=1)
    other_version = FileVersion.objects.create(file_name="gamma.txt", version_number=2)

    UserFileVersion.objects.create(fileversion=first, user=user)
    UserFileVersion.objects.create(fileversion=second, user=user)
    other_user = user_factory()
    UserFileVersion.objects.create(fileversion=other_version, user=other_user)

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/files/user/")

    assert response.status_code == 200
    assert response.json() == [
        {"file_name": "alpha.txt", "version": 0},
        {"file_name": "beta.txt", "version": 1},
    ]
