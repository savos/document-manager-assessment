from django.urls import path

from .views import LoginView, RegisterView, UserView

app_name = "accounts"

urlpatterns = [
    path("signup/", RegisterView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", UserView.as_view(), name="me"),
]
