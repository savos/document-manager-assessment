from propylon_document_manager.file_versions.models import FileVersion, UserFileVersion
from .factories import UserFactory

def test_file_versions():
    file_name = "new_file"
    file_version = 1
    FileVersion.objects.create(
        file_name=file_name,
        version_number=file_version
    )
    files = FileVersion.objects.all()
    assert files.count() == 1
    assert files[0].file_name == file_name
    assert files[0].version_number == file_version


def test_user_fileversion():
    user = UserFactory()
    file_version = FileVersion.objects.create(
        file_name="another_file", version_number=0
    )
    mapping = UserFileVersion.objects.create(fileversion=file_version, user=user)
    assert mapping.fileversion == file_version
    assert mapping.user == user
    assert mapping.created_at is not None
    assert mapping.updated_at is not None
    assert mapping.deleted_at is None
