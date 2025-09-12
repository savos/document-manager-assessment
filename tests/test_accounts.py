import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_user_can_register():
    client = APIClient()
    response = client.post(
        "/api/accounts/signup/",
        {
            "email": "tester@example.com",
            "name": "Test User",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        },
        format="json",
    )
    assert response.status_code == 201
    assert User.objects.filter(email="tester@example.com").exists()


@pytest.mark.django_db
def test_user_can_login(user_factory):
    user = user_factory(password="StrongPass123!")
    client = APIClient()
    response = client.post(
        "/api/accounts/login/",
        {"email": user.email, "password": "StrongPass123!"},
        format="json",
    )
    assert response.status_code == 200
    assert "token" in response.json()
