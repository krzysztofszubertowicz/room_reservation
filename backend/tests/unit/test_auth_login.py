import pytest


def test_login_with_valid_credentials(client, seeded_entities):
    email = seeded_entities["regular_user"].email

    response = client.post(
        "/login",
        data={"username": email, "password": "user-pass"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["user"]["email"] == email
    assert payload["access_token"]


@pytest.mark.parametrize(
    ("username", "password"),
    [
        ("user@example.com", "wrong-pass"),
        ("missing@example.com", "any-pass"),
    ],
)
def test_login_rejects_invalid_credentials(client, username, password):
    response = client.post(
        "/login",
        data={"username": username, "password": password},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid login credentials"
