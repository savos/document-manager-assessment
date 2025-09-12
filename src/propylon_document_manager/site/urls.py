from django.conf import settings
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from .views import HealthCheckView

# API URLs
urlpatterns = [
    path("api/accounts/", include("propylon_document_manager.accounts.urls")),
    path("api/health/", HealthCheckView.as_view(), name="health"),
    path("api/", include("propylon_document_manager.site.api_router")),
    path("api-auth/", include("rest_framework.urls")),
    path("auth-token/", obtain_auth_token),
]

if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
