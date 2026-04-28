from src.core.constants import (
    ACTOR_NOT_FOUND,
    MOVIE_EXISTS,
    MOVIE_HAS_RATE,
    MOVIE_NOT_FOUND,
)

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


def test_create_movie_rating(client, movie_without_rating, user, token):
    payload = {'rating': 1}
    response = client.post(
        f'{URL_PREFIX}/{movie_without_rating.id}/ratings',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == 201

    data = response.json()

    assert data['user_id'] == user.id
    assert data['movie_id'] == movie_without_rating.id
    assert data['rating'] == payload['rating']
    assert 'created_at' in data
    assert 'updated_at' in data


def test_create_movie_rating_without_auth(client, movie_without_rating):
    payload = {'rating': 1}
    response = client.post(
        f'{URL_PREFIX}/{movie_without_rating.id}/ratings',
        json=payload,
    )

    assert response.status_code == 401


def test_create_movie_rating_with_nonexistent_movie(client, user, token):
    payload = {'rating': 1}
    response = client.post(
        f'{URL_PREFIX}/999/ratings',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == 404

    data = response.json()

    assert data['detail'] == MOVIE_NOT_FOUND


def test_create_movie_rating_with_movie_rated(client, movie_rated, token):
    payload = {'rating': 1}
    response = client.post(
        f'{URL_PREFIX}/{movie_rated.movie_id}/ratings',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == 409

    data = response.json()

    assert data['detail'] == MOVIE_HAS_RATE


def test_update_movie_rating(client, movie_rated, token):
    payload = {'rating': 2}
    response = client.put(
        f'{URL_PREFIX}/{movie_rated.movie_id}/ratings',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == 200

    data = response.json()
    assert data['user_id'] == movie_rated.user_id
    assert data['movie_id'] == movie_rated.movie_id
    assert data['rating'] == payload['rating']
    assert 'updated_at' in data


def test_update_movie_rating_without_auth(client, movie_rated):
    payload = {'rating': 2}
    response = client.put(
        f'{URL_PREFIX}/{movie_rated.movie_id}/ratings',
        json=payload,
    )

    assert response.status_code == 401


def test_update_movie_rating_witout_movie(client, movie_rated, token):
    payload = {'rating': 2}
    response = client.put(
        f'{URL_PREFIX}/999/ratings',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
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


def test_list_movies(
    client, movie, movie_without_rating, movie_without_cast, movie_rated
):
    response = client.get(f'{URL_PREFIX}?limit=4&offset=0')

    assert response.status_code == 200

    data = response.json()
    assert data['limit'] == 4
    assert data['offset'] == 0

    movies = data['movies']
    assert len(movies) == 3

    movies_by_id = {m['id']: m for m in movies}

    m = movies_by_id[movie.id]
    assert m['name'] == movie.name
    assert m['rating'] == movie.user_movies[0].rating
    assert len(m['cast']) == len(movie.actors)

    m = movies_by_id[movie_without_rating.id]
    assert m['name'] == movie_without_rating.name
    assert m['rating'] == movie_rated.rating
    assert len(m['cast']) == len(movie_without_rating.actors)

    m = movies_by_id[movie_without_cast.id]
    assert m['name'] == movie_without_cast.name
    assert m['cast'] == []


def test_list_movies_with_name_filter(
    client, movie, movie_without_rating, movie_without_cast, movie_rated
):
    response = client.get(f'{URL_PREFIX}?name_filter=without_cast')

    assert response.status_code == 200

    data = response.json()
    movies = data['movies']
    assert len(movies) == 1
    assert movies[0]['id'] == movie_without_cast.id
    assert movies[0]['name'] == movie_without_cast.name


def test_list_movies_with_rating_filter(
    client, movie, movie_without_rating, movie_without_cast
):
    # movie_without_rating has no rating here (movie_rated fixture not used)
    response = client.get(f'{URL_PREFIX}?rating_filter=10')

    assert response.status_code == 200

    data = response.json()
    movies = data['movies']
    assert len(movies) == 2

    returned_ids = {m['id'] for m in movies}
    assert movie.id in returned_ids
    assert movie_without_cast.id in returned_ids
    assert movie_without_rating.id not in returned_ids


def test_list_movies_with_name_and_rating_filter(
    client, movie, movie_without_rating, movie_without_cast
):
    # 'without' matches movie_without_rating and movie_without_cast
    # but only movie_without_cast has a rating
    response = client.get(f'{URL_PREFIX}?name_filter=without&rating_filter=10')

    assert response.status_code == 200

    data = response.json()
    movies = data['movies']
    assert len(movies) == 1
    assert movies[0]['id'] == movie_without_cast.id


def test_update_movie(client, movie_without_cast, actor, other_actor):
    payload = {
        'name': 'test_update_movie_name',
        'synopsis': 'test_update_movie_synopsis',
        'director': 'test_update_movie_director',
        'cast_ids': [actor.id, other_actor.id],
        'release_date': '2000-01-01',
    }

    response = client.put(
        f'{URL_PREFIX}/{movie_without_cast.id}', json=payload
    )

    assert response.status_code == 200

    data = response.json()
    assert data['id'] == movie_without_cast.id
    assert data['name'] == payload['name']
    assert data['synopsis'] == payload['synopsis']
    assert data['director'] == payload['director']
    assert data['release_date'] == payload['release_date']
    assert len(data['cast']) == 2
    assert data['cast'][0]['id'] == actor.id
    assert data['cast'][0]['name'] == actor.name
    assert data['cast'][0]['age'] == actor.age
    assert data['cast'][1]['id'] == other_actor.id
    assert data['cast'][1]['name'] == other_actor.name
    assert data['cast'][1]['age'] == other_actor.age
    assert 'updated_at' in data


def test_update_noexistent_movie(client, actor, other_actor):
    payload = {
        'name': 'test_update_movie_name',
        'synopsis': 'test_update_movie_synopsis',
        'director': 'test_update_movie_director',
        'cast_ids': [actor.id, other_actor.id],
        'release_date': '2000-01-01',
    }

    response = client.put(f'{URL_PREFIX}/999', json=payload)

    assert response.status_code == 404

    data = response.json()

    assert data['detail'] == MOVIE_NOT_FOUND


def test_update_movie_existent_name(
    client, movie, movie_without_cast, actor, other_actor
):
    payload = {
        'name': movie_without_cast.name,
        'synopsis': 'test_update_movie_synopsis',
        'director': 'test_update_movie_director',
        'cast_ids': [actor.id, other_actor.id],
        'release_date': '2000-01-01',
    }

    response = client.put(f'{URL_PREFIX}/{movie.id}', json=payload)

    assert response.status_code == 409

    data = response.json()

    assert data['detail'] == MOVIE_EXISTS


def test_update_movie_actor_not_exists(
    client, movie_without_cast, actor, other_actor
):
    payload = {
        'name': 'test_update_movie_name',
        'synopsis': 'test_update_movie_synopsis',
        'director': 'test_update_movie_director',
        'cast_ids': [actor.id, other_actor.id, 999],
        'release_date': '2000-01-01',
    }

    response = client.put(
        f'{URL_PREFIX}/{movie_without_cast.id}', json=payload
    )

    assert response.status_code == 404

    data = response.json()

    assert data['detail'] == f'{ACTOR_NOT_FOUND}: {{999}}'


def test_update_movie_actor_without_update_cast(client, movie):
    actors = list(movie.actors)
    payload = {
        'name': 'test_update_movie_name',
        'synopsis': 'test_update_movie_synopsis',
        'director': 'test_update_movie_director',
        'release_date': '2000-01-01',
    }

    response = client.put(f'{URL_PREFIX}/{movie.id}', json=payload)

    data = response.json()
    assert data['id'] == movie.id
    assert data['name'] == payload['name']
    assert data['synopsis'] == payload['synopsis']
    assert data['director'] == payload['director']
    assert data['release_date'] == payload['release_date']
    assert len(data['cast']) == len(actors)
    cast_by_id = {a['id']: a for a in data['cast']}
    for actor in actors:
        assert actor.id in cast_by_id
        assert cast_by_id[actor.id]['name'] == actor.name
        assert cast_by_id[actor.id]['age'] == actor.age
    assert 'updated_at' in data
