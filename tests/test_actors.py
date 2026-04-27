from src.services.actors import ACTOR_EXISTS, ACTOR_NOT_FOUND

URL_PREFIX = '/api/v1/actors'


def test_create_actor(client):
    payload = {'name': 'test_create_actor', 'age': 18}
    response = client.post(URL_PREFIX, json=payload)

    assert response.status_code == 201

    data = response.json()

    assert 'id' in data
    assert data['name'] == payload['name']
    assert data['age'] == payload['age']
    assert 'created_at' in data
    assert 'updated_at' in data


def test_create_actor_with_existent_actor(client, actor):
    payload = {'name': actor.name, 'age': actor.age}
    response = client.post(URL_PREFIX, json=payload)

    assert response.status_code == 409

    data = response.json()

    assert data['detail'] == ACTOR_EXISTS


def test_get_actor(client, actor):
    response = client.get(f'{URL_PREFIX}/{actor.id}')

    assert response.status_code == 200

    data = response.json()

    assert 'id' in data
    assert data['name'] == actor.name
    assert data['age'] == actor.age
    assert 'created_at' in data
    assert 'updated_at' in data


def test_get_noexistent_actor(client):
    response = client.get(f'{URL_PREFIX}/999')

    assert response.status_code == 404

    data = response.json()

    assert data['detail'] == ACTOR_NOT_FOUND


def test_delete_actor(client, actor):
    response = client.delete(f'{URL_PREFIX}/{actor.id}')

    assert response.status_code == 204


def test_delete_noexistent_actor(client):
    response = client.delete(f'{URL_PREFIX}/999')

    assert response.status_code == 404

    data = response.json()

    assert data['detail'] == ACTOR_NOT_FOUND


def test_list_actors(client, actor, other_actor):
    response = client.get(URL_PREFIX)

    assert response.status_code == 200

    data = response.json()
    actors = data['actors']

    assert len(actors) >= 2

    actor_data = next(a for a in actors if a['id'] == actor.id)
    assert actor_data['name'] == actor.name
    assert actor_data['age'] == actor.age
    assert 'created_at' in actor_data
    assert 'updated_at' in actor_data

    other_actor_data = next(a for a in actors if a['id'] == other_actor.id)
    assert other_actor_data['name'] == other_actor.name
    assert other_actor_data['age'] == other_actor.age
    assert 'created_at' in other_actor_data
    assert 'updated_at' in other_actor_data

    assert 'limit' in data
    assert 'offset' in data


def test_list_actors_with_search_filter(client, actor, other_actor):
    response = client.get(f'{URL_PREFIX}?limit=2&offset=0&search_filter=other')

    assert response.status_code == 200

    data = response.json()
    actors = data['actors']

    assert len(actors) == 1

    actor_data = actors[0]
    assert actor_data['id'] == other_actor.id
    assert actor_data['name'] == other_actor.name
    assert actor_data['age'] == other_actor.age
    assert 'created_at' in actor_data
    assert 'updated_at' in actor_data

    assert 'limit' in data
    assert 'offset' in data


def test_list_actors_without_actors(client):
    response = client.get(URL_PREFIX)

    assert response.status_code == 200

    data = response.json()
    actors = data['actors']

    assert len(actors) == 0

    assert 'limit' in data
    assert 'offset' in data


def test_update_actor(client, actor):
    payload = {'name': 'updated_actor', 'age': 30}
    response = client.put(f'{URL_PREFIX}/{actor.id}', json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data['id'] == actor.id
    assert data['name'] == payload['name']
    assert data['age'] == payload['age']
    assert 'created_at' in data
    assert 'updated_at' in data


def test_update_actor_only_name(client, actor):
    payload = {'name': 'updated_actor_name_only'}
    response = client.put(f'{URL_PREFIX}/{actor.id}', json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data['id'] == actor.id
    assert data['name'] == payload['name']
    assert data['age'] == actor.age


def test_update_actor_only_age(client, actor):
    payload = {'age': 99}
    response = client.put(f'{URL_PREFIX}/{actor.id}', json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data['id'] == actor.id
    assert data['name'] == actor.name
    assert data['age'] == payload['age']


def test_update_noexistent_actor(client):
    payload = {'name': 'ghost_actor', 'age': 25}
    response = client.put(f'{URL_PREFIX}/999', json=payload)

    assert response.status_code == 404

    data = response.json()

    assert data['detail'] == ACTOR_NOT_FOUND


def test_update_actor_with_existent_name(client, actor, other_actor):
    payload = {'name': other_actor.name}
    response = client.put(f'{URL_PREFIX}/{actor.id}', json=payload)

    assert response.status_code == 409

    data = response.json()

    assert data['detail'] == ACTOR_EXISTS
