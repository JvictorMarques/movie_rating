from src.services.actors import ACTOR_NOT_FOUND
from src.services.movies import MOVIE_EXISTS, MOVIE_HAS_RATE, MOVIE_NOT_FOUND
from src.services.users import USER_NOT_FOUND

URL_PREFIX = '/api/v1/movies'


def test_create_movie_without_cast(client):
    payload = {
        'name': 'test_create_movie_without_cast',
        'synopsis': 'test_create_movie_without_cast_synopsis',
        'director': 'test_create_movie_without_cast_director',
        'release_date': '2000-01-01',
    }
    response = client.post(URL_PREFIX, json=payload)

    assert response.status_code == 201

    data = response.json()
    assert 'id' in data
    assert data['name'] == payload['name']
    assert data['synopsis'] == payload['synopsis']
    assert data['director'] == payload['director']
    assert data['release_date'] == payload['release_date']
    assert data['cast'] is None
    assert 'created_at' in data
    assert 'updated_at' in data


def test_create_movie_with_existing_name(client, movie):
    payload = {
        'name': movie.name,
        'synopsis': 'test_create_movie_with_existing_name_synopsis',
        'director': 'test_create_movie_with_existing_name_director',
        'release_date': '2000-01-01',
    }
    response = client.post(URL_PREFIX, json=payload)

    assert response.status_code == 409

    data = response.json()
    assert data['detail'] == MOVIE_EXISTS


def test_create_movie_with_cast(client, actor, other_actor):
    payload = {
        'name': 'test_create_movie_with_cast',
        'synopsis': 'test_create_movie_with_cast_synopsis',
        'director': 'test_create_movie_with_cast_director',
        'cast_ids': [actor.id, other_actor.id],
        'release_date': '2000-01-01',
    }
    response = client.post(URL_PREFIX, json=payload)

    assert response.status_code == 201

    data = response.json()
    assert 'id' in data
    assert data['name'] == payload['name']
    assert data['synopsis'] == payload['synopsis']
    assert data['director'] == payload['director']
    assert data['release_date'] == payload['release_date']

    assert data['cast'][0]['id'] == actor.id
    assert data['cast'][0]['name'] == actor.name
    assert data['cast'][0]['age'] == actor.age

    assert data['cast'][1]['id'] == other_actor.id
    assert data['cast'][1]['name'] == other_actor.name
    assert data['cast'][1]['age'] == other_actor.age

    assert 'created_at' in data
    assert 'updated_at' in data


def test_create_movie_with_nonexistent_actor(client, actor, other_actor):
    payload = {
        'name': 'test_create_movie_with_nonexistent_actor',
        'synopsis': 'test_create_movie_with_nonexistent_actor_synopsis',
        'director': 'test_create_movie_with_nonexistent_actor_director',
        'cast_ids': [actor.id, other_actor.id, 3],
        'release_date': '2000-01-01',
    }
    response = client.post(URL_PREFIX, json=payload)

    assert response.status_code == 404

    data = response.json()
    assert data['detail'] == f'{ACTOR_NOT_FOUND}: {{3}}'


def test_create_movie_rating(client, movie_without_rating, user):
    payload = {'rating': 1}
    response = client.post(
        f'{URL_PREFIX}/{movie_without_rating.id}/ratings?current_user_id={user.id}',
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data['user_id'] == user.id
    assert data['movie_id'] == movie_without_rating.id
    assert data['rating'] == payload['rating']
    assert 'created_at' in data
    assert 'updated_at' in data


def test_create_movie_rating_with_nonexistent_user(
    client, movie_without_rating
):
    payload = {'rating': 1}
    response = client.post(
        f'{URL_PREFIX}/{movie_without_rating.id}/ratings?current_user_id=1',
        json=payload,
    )

    assert response.status_code == 404

    data = response.json()

    assert data['detail'] == USER_NOT_FOUND


def test_create_movie_rating_with_nonexistent_movie(client, user):
    payload = {'rating': 1}
    response = client.post(
        f'{URL_PREFIX}/1/ratings?current_user_id={user.id}', json=payload
    )

    assert response.status_code == 404

    data = response.json()

    assert data['detail'] == MOVIE_NOT_FOUND


def test_create_movie_rating_with_movie_rated(client, movie_rated):
    payload = {'rating': 1}
    url = (
        f'{URL_PREFIX}/{movie_rated.movie_id}'
        f'/ratings?current_user_id={movie_rated.user_id}'
    )
    response = client.post(url, json=payload)

    assert response.status_code == 409

    data = response.json()

    assert data['detail'] == MOVIE_HAS_RATE


def test_update_movie_rating(client, movie_rated):
    payload = {'rating': 2}
    url = (
        f'{URL_PREFIX}/{movie_rated.movie_id}'
        f'/ratings?current_user_id={movie_rated.user_id}'
    )
    response = client.put(url, json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data['user_id'] == movie_rated.user_id
    assert data['movie_id'] == movie_rated.movie_id
    assert data['rating'] == payload['rating']
    assert 'updated_at' in data


def test_update_movie_rating_witout_user(client, movie_rated):
    payload = {'rating': 2}
    response = client.put(
        f'{URL_PREFIX}/{movie_rated.movie_id}/ratings?current_user_id=2',
        json=payload,
    )

    assert response.status_code == 404

    data = response.json()

    assert data['detail'] == USER_NOT_FOUND


def test_update_movie_rating_witout_movie(client, movie_rated):
    payload = {'rating': 2}
    response = client.put(
        f'{URL_PREFIX}/2/ratings?current_user_id={movie_rated.user_id}',
        json=payload,
    )

    assert response.status_code == 404

    data = response.json()

    assert data['detail'] == MOVIE_NOT_FOUND


def test_get_movie(client, movie):
    response = client.get(f'{URL_PREFIX}/{movie.id}')

    assert response.status_code == 200

    data = response.json()

    assert data['id'] == movie.id
    assert data['name'] == movie.name
    assert data['synopsis'] == movie.synopsis
    assert data['director'] == movie.director
    assert data['release_date'] == str(movie.release_date)
    assert data['rating'] == movie.user_movies[0].rating

    assert len(data['cast']) == len(movie.actors)

    cast_by_id = {a['id']: a for a in data['cast']}
    for actor in movie.actors:
        assert actor.id in cast_by_id
        assert cast_by_id[actor.id]['name'] == actor.name
        assert cast_by_id[actor.id]['age'] == actor.age

    assert 'created_at' in data
    assert 'updated_at' in data


def test_get_nonexistent_movie(client):
    response = client.get(f'{URL_PREFIX}/1')

    assert response.status_code == 404

    data = response.json()

    assert data['detail'] == MOVIE_NOT_FOUND


def test_delete_movie(client, movie):
    response = client.delete(f'{URL_PREFIX}/{movie.id}')

    assert response.status_code == 204


def test_delete_nonexistent_movie(client):
    response = client.delete(f'{URL_PREFIX}/1')

    assert response.status_code == 404

    data = response.json()

    assert data['detail'] == MOVIE_NOT_FOUND
