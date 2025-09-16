import pytest

from propylon_document_manager.file_versions.models import User
from .factories import UserFactory

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass

@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory()


@pytest.fixture
def user_factory(db):
    """Return a callable that creates users with optional custom fields."""

    def factory(**kwargs) -> User:
        password = kwargs.pop("password", None)
        if password is not None:
            return UserFactory(password=password, **kwargs)
        return UserFactory(**kwargs)

    return factory
