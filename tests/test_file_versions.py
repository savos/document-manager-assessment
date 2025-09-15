from propylon_document_manager.file_versions.models import FileVersion, UserFileVersion
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
