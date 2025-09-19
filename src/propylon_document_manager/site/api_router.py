from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from propylon_document_manager.file_versions.api.views import (
    FileListView,
    FileUploadView,
    FileVersionViewSet,
    UserFileListView,
)

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("file_versions", FileVersionViewSet)


app_name = "api"
urlpatterns = router.urls + [
    path("file-uploads/", FileUploadView.as_view(), name="file-upload"),
    path("files/user/", UserFileListView.as_view(), name="user-file-list"),
    path("files/", FileListView.as_view(), name="file-list"),
]
