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


def test_create_user_duplicate_email(client, user):
    payload = {
        'name': 'test_user',
        'email': 'test_user@email.com',
        'age': 18,
        'password': 'Teste123@',  # NOSONAR
    }
    response = client.post(URL_PREFIX, json=payload)
    assert response.status_code == 409

    data = response.json()
    assert data['detail'] == 'Email already exists'


def test_delete_user(client, user):
    response = client.delete(f'{URL_PREFIX}/{user.id}')
    assert response.status_code == 204


def test_delete_user_that_not_exists(client):
    response = client.delete(f'{URL_PREFIX}/1')
    assert response.status_code == 404

    data = response.json()
    assert data['detail'] == 'User not found'


def test_get_user(client, user):
    response = client.get(f'{URL_PREFIX}/{user.id}')

    assert response.status_code == 200

    data = response.json()

    assert data['id'] == user.id
    assert data['name'] == user.name
    assert data['email'] == user.email
    assert data['age'] == user.age


def test_get_user_that_not_exists(client):
    response = client.get(f'{URL_PREFIX}/1')
    assert response.status_code == 404

    data = response.json()
    assert data['detail'] == 'User not found'


def test_list_users(client, user, other_user):
    response = client.get(f'{URL_PREFIX}?limit=2&offset=0')

    assert response.status_code == 200

    data = response.json()
    assert len(data['users']) == 2

    assert data['users'][0]['id'] == user.id
    assert data['users'][0]['name'] == user.name
    assert data['users'][0]['email'] == user.email
    assert data['users'][0]['age'] == user.age

    assert data['users'][1]['id'] == other_user.id
    assert data['users'][1]['name'] == other_user.name
    assert data['users'][1]['email'] == other_user.email
    assert data['users'][1]['age'] == other_user.age

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

    assert data['limit'] == 2
    assert data['offset'] == 0
