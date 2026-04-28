import jwt
import pytest

from src.core.constants import USER_NOT_FOUND
from src.core.security import create_access_token
from src.core.settings import Settings

URL_PREFIX = '/api/v1/auth'
USERS_PREFIX = '/api/v1/users'

settings = Settings()

_LOGIN_EMAIL = 'auth_test@email.com'
_LOGIN_PASSWORD = 'Teste123@'  # NOSONAR


@pytest.fixture
def registered_user(client):
    payload = {
        'name': 'auth_test_user',
        'email': _LOGIN_EMAIL,
        'age': 25,
        'password': _LOGIN_PASSWORD,
    }
    response = client.post(USERS_PREFIX, json=payload)
    assert response.status_code == 201
    return response.json()


def test_login_success(client, registered_user):
    payload = {'email': _LOGIN_EMAIL, 'password': _LOGIN_PASSWORD}
    response = client.post(f'{URL_PREFIX}/token', json=payload)

    assert response.status_code == 200

    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'


def test_login_wrong_password(client, registered_user):
    payload = {'email': _LOGIN_EMAIL, 'password': 'WrongPass1@'}  # NOSONAR
    response = client.post(f'{URL_PREFIX}/token', json=payload)

    assert response.status_code == 401
    assert response.json()['detail'] == 'Incorrect email or password'


def test_login_wrong_email(client):
    payload = {
        'email': 'nonexistent@email.com',
        'password': _LOGIN_PASSWORD,
    }
    response = client.post(f'{URL_PREFIX}/token', json=payload)

    assert response.status_code == 401
    assert response.json()['detail'] == 'Incorrect email or password'


def test_refresh_token(client, registered_user):
    token = create_access_token(data={'sub': str(registered_user['id'])})
    response = client.post(
        f'{URL_PREFIX}/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == 200

    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'


def test_refresh_token_without_auth(client):
    response = client.post(f'{URL_PREFIX}/refresh_token')
    assert response.status_code == 401


def test_access_with_expired_token(client, registered_user):
    expired_payload = {'sub': str(registered_user['id']), 'exp': 0}
    expired_token = jwt.encode(
        expired_payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    response = client.post(
        f'{URL_PREFIX}/refresh_token',
        headers={'Authorization': f'Bearer {expired_token}'},
    )

    assert response.status_code == 401
    assert response.json()['detail'] == 'Token has expired'


def test_access_with_invalid_token(client):
    response = client.post(
        f'{URL_PREFIX}/refresh_token',
        headers={'Authorization': 'Bearer invalid.token.here'},
    )

    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid token'


def test_access_token_without_sub(client, registered_user):
    token_no_sub = create_access_token(data={'data': 'no_sub'})
    response = client.post(
        f'{URL_PREFIX}/refresh_token',
        headers={'Authorization': f'Bearer {token_no_sub}'},
    )

    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid token'


def test_access_token_with_non_int_sub(client):
    token_bad_sub = create_access_token(data={'sub': 'not_a_number'})
    response = client.post(
        f'{URL_PREFIX}/refresh_token',
        headers={'Authorization': f'Bearer {token_bad_sub}'},
    )

    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid token'


def test_access_token_user_not_found(client):
    token_gone = create_access_token(data={'sub': '99999'})
    response = client.post(
        f'{URL_PREFIX}/refresh_token',
        headers={'Authorization': f'Bearer {token_gone}'},
    )

    assert response.status_code == 404
    assert response.json()['detail'] == USER_NOT_FOUND
