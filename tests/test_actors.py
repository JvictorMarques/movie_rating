from src.services.actors import ACTOR_EXISTS

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
