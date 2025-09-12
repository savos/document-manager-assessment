from django.http import HttpResponse
from django.views import View


class HealthCheckView(View):
    """Return a simple response to verify the server is running."""

    def get(self, request):
        return HttpResponse("OK")
