from src.core.constants import EMAIL_EXISTS, FORBIDDEN, USER_NOT_FOUND

URL_PREFIX = '/api/v1/users'


def test_create_user(client):
    payload = {
        'name': 'test_create_user',
        'email': 'test_create_user@email.com',
        'age': 18,
        'password': 'Teste123@',  # NOSONAR
    }
    response = client.post(URL_PREFIX, json=payload)
    assert response.status_code == 201

    data = response.json()
    assert 'id' in data
    assert data['name'] == payload['name']
    assert data['email'] == payload['email']
    assert data['age'] == payload['age']
    assert 'password' not in data
    assert 'created_at' in data
    assert 'updated_at' in data


def test_create_user_duplicate_email(client, user):
    payload = {
        'name': 'test_create_user',
        'email': user.email,
        'age': 18,
        'password': 'Teste123@',  # NOSONAR
    }
    response = client.post(URL_PREFIX, json=payload)
    assert response.status_code == 409

    data = response.json()
    assert data['detail'] == EMAIL_EXISTS


def test_delete_user(client, user, token):
    response = client.delete(
        f'{URL_PREFIX}/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == 204


def test_delete_user_forbidden(client, user, other_user, token):
    response = client.delete(
        f'{URL_PREFIX}/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == 403

    data = response.json()
    assert data['detail'] == FORBIDDEN


def test_get_user(client, user):
    response = client.get(f'{URL_PREFIX}/{user.id}')

    assert response.status_code == 200

    data = response.json()

    assert data['id'] == user.id
    assert data['name'] == user.name
    assert data['email'] == user.email
    assert data['age'] == user.age
    assert 'password' not in data
    assert 'created_at' in data
    assert 'updated_at' in data


def test_get_user_that_not_exists(client):
    response = client.get(f'{URL_PREFIX}/999')
    assert response.status_code == 404

    data = response.json()
    assert data['detail'] == USER_NOT_FOUND


def test_list_users(client, user, other_user):
    response = client.get(f'{URL_PREFIX}?limit=2&offset=0')

    assert response.status_code == 200

    data = response.json()
    assert len(data['users']) == 2

    assert data['users'][0]['id'] == user.id
    assert data['users'][0]['name'] == user.name
    assert data['users'][0]['email'] == user.email
    assert data['users'][0]['age'] == user.age
    assert 'password' not in data['users'][0]
    assert 'created_at' in data['users'][0]
    assert 'updated_at' in data['users'][0]

    assert data['users'][1]['id'] == other_user.id
    assert data['users'][1]['name'] == other_user.name
    assert data['users'][1]['email'] == other_user.email
    assert data['users'][1]['age'] == other_user.age
    assert 'password' not in data['users'][1]
    assert 'created_at' in data['users'][1]
    assert 'updated_at' in data['users'][1]

    assert data['limit'] == 2
    assert data['offset'] == 0


def test_list_users_with_filter(client, user, other_user):
    response = client.get(f'{URL_PREFIX}?limit=2&offset=0&search_filter=other')

    assert response.status_code == 200

    data = response.json()
    assert len(data['users']) == 1

    assert data['users'][0]['id'] == other_user.id
    assert data['users'][0]['name'] == other_user.name
    assert data['users'][0]['email'] == other_user.email
    assert data['users'][0]['age'] == other_user.age
    assert 'password' not in data['users'][0]
    assert 'created_at' in data['users'][0]
    assert 'updated_at' in data['users'][0]

    assert data['limit'] == 2
    assert data['offset'] == 0


def test_update_user_name(client, user, token):
    payload = {'name': 'test_update_user'}
    response = client.put(
        f'{URL_PREFIX}/{user.id}',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == 200

    data = response.json()

    assert 'id' in data
    assert data['name'] == payload['name']
    assert data['email'] == user.email
    assert data['age'] == user.age
    assert 'password' not in data
    assert 'created_at' in data
    assert 'updated_at' in data


def test_update_user_email(client, user, token):
    payload = {'email': 'new_email@email.com'}
    response = client.put(
        f'{URL_PREFIX}/{user.id}',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == 200

    data = response.json()

    assert 'id' in data
    assert data['name'] == user.name
    assert data['email'] == payload['email']
    assert data['age'] == user.age
    assert 'password' not in data
    assert 'created_at' in data
    assert 'updated_at' in data


def test_update_user_age(client, user, token):
    payload = {'age': 30}
    response = client.put(
        f'{URL_PREFIX}/{user.id}',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == 200

    data = response.json()

    assert 'id' in data
    assert data['name'] == user.name
    assert data['email'] == user.email
    assert data['age'] == payload['age']
    assert 'password' not in data
    assert 'created_at' in data
    assert 'updated_at' in data


def test_update_user_password(client, user, token):
    payload = {'password': 'NewPass456@'}  # NOSONAR
    response = client.put(
        f'{URL_PREFIX}/{user.id}',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == 200

    data = response.json()

    assert 'id' in data
    assert data['name'] == user.name
    assert data['email'] == user.email
    assert data['age'] == user.age
    assert 'password' not in data
    assert 'created_at' in data
    assert 'updated_at' in data


def test_update_user_email_exists(client, user, other_user, token):
    payload = {'email': other_user.email}
    response = client.put(
        f'{URL_PREFIX}/{user.id}',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == 409
    data = response.json()

    assert data['detail'] == EMAIL_EXISTS


def test_update_user_forbidden(client, user, other_user, token):
    payload = {'name': 'ghost'}
    response = client.put(
        f'{URL_PREFIX}/{other_user.id}',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == 403

    data = response.json()
    assert data['detail'] == FORBIDDEN
