import asyncio
import random
import time

import httpx

BASE = 'http://localhost:8000/api/v1'


async def delay(min_ms: int = 10, max_ms: int = 500) -> None:
    await asyncio.sleep(random.randint(min_ms, max_ms) / 1000)


async def create_users(client: httpx.AsyncClient) -> list[dict]:
    users_data = [
        {
            'name': 'Alice Silva',
            'email': 'alice@example.com',
            'age': 28,
            'password': 'senha123',
        },
        {
            'name': 'Bruno Costa',
            'email': 'bruno@example.com',
            'age': 34,
            'password': 'senha123',
        },
        {
            'name': 'Carla Mendes',
            'email': 'carla@example.com',
            'age': 22,
            'password': 'senha123',
        },
    ]
    users = []
    for data in users_data:
        await delay(50, 300)
        r = await client.post(f'{BASE}/users/', json=data)
        if r.status_code == 201:
            users.append(r.json())
            print(f'  [+] Usuário criado: {r.json()["name"]}')
        else:
            print(
                f'  [!] Usuário já existe ou erro:'
                f' {data["email"]} — {r.status_code}'
            )
    return users


async def create_actors(client: httpx.AsyncClient) -> list[dict]:
    actors_data = [
        {'name': 'Leonardo DiCaprio', 'age': 49},
        {'name': 'Margot Robbie', 'age': 33},
        {'name': 'Cillian Murphy', 'age': 47},
        {'name': 'Ana de Armas', 'age': 35},
    ]
    actors = []
    for data in actors_data:
        await delay(20, 150)
        r = await client.post(f'{BASE}/actors/', json=data)
        if r.status_code == 201:
            actors.append(r.json())
            print(f'  [+] Ator criado: {r.json()["name"]}')
        else:
            print(f'  [!] Erro ao criar ator {data["name"]}: {r.status_code}')
    return actors


async def create_movies(
    client: httpx.AsyncClient, actor_ids: list[int]
) -> list[dict]:
    movies_data = [
        {
            'name': 'Inception',
            'synopsis': 'Um ladrão que rouba segredos por meio de sonhos.',
            'director': 'Christopher Nolan',
            'cast_ids': actor_ids[:2],
            'release_date': '2010-07-16',
        },
        {
            'name': 'Oppenheimer',
            'synopsis': 'A história do pai da bomba atômica.',
            'director': 'Christopher Nolan',
            'cast_ids': actor_ids[2:],
            'release_date': '2023-07-21',
        },
        {
            'name': 'Barbie',
            'synopsis': 'Barbie e Ken vão ao mundo real.',
            'director': 'Greta Gerwig',
            'cast_ids': actor_ids[1:3],
            'release_date': '2023-07-21',
        },
    ]
    movies = []
    for data in movies_data:
        await delay(100, 500)
        r = await client.post(f'{BASE}/movies/', json=data)
        if r.status_code == 201:
            movies.append(r.json())
            print(f'  [+] Filme criado: {r.json()["name"]}')
        else:
            print(f'  [!] Erro ao criar filme {data["name"]}: {r.status_code}')
    return movies


async def authenticate(
    client: httpx.AsyncClient, email: str, password: str
) -> str | None:
    await delay(10, 80)
    r = await client.post(
        f'{BASE}/auth/token', json={'email': email, 'password': password}
    )
    if r.status_code == 200:
        return r.json()['access_token']
    print(f'  [!] Falha no login de {email}: {r.status_code}')
    return None


async def rate_movies(
    client: httpx.AsyncClient, token: str, movie_ids: list[int]
) -> None:
    headers = {'Authorization': f'Bearer {token}'}
    for movie_id in movie_ids:
        rating = round(random.uniform(1.0, 5.0), 1)
        await delay(80, 400)
        r = await client.post(
            f'{BASE}/movies/{movie_id}/ratings',
            json={'rating': rating},
            headers=headers,
        )
        if r.status_code in {200, 201}:
            print(f'  [+] Rating {rating} no filme {movie_id}')
        else:
            await delay(10, 50)
            r = await client.put(
                f'{BASE}/movies/{movie_id}/ratings',
                json={'rating': rating},
                headers=headers,
            )
            if r.status_code == 200:
                print(
                    f'  [~] Rating atualizado para {rating}'
                    f' no filme {movie_id}'
                )


async def query_data(client: httpx.AsyncClient) -> None:
    endpoints = [
        f'{BASE}/movies/',
        f'{BASE}/users/',
        f'{BASE}/actors/',
    ]
    for url in endpoints:
        await delay(30, 200)
        r = await client.get(url)
        data = r.json()
        count = (
            len(data) if isinstance(data, list) else len(data.get('items', []))
        )
        print(f'  [?] GET {url} → {r.status_code} ({count} itens)')


async def simulate_errors(client: httpx.AsyncClient) -> None:
    await delay(10, 50)
    r = await client.get(f'{BASE}/movies/99999')
    print(f'  [4xx] GET movie/99999 → {r.status_code}')

    await delay(10, 50)
    r = await client.post(
        f'{BASE}/users/',
        json={'name': 'x', 'email': 'invalido', 'age': -1, 'password': ''},
    )
    print(f'  [4xx] POST user inválido → {r.status_code}')


async def main() -> None:
    async with httpx.AsyncClient(timeout=30) as client:
        print('\n=== Criando usuários ===')
        await create_users(client)

        print('\n=== Criando atores ===')
        actors = await create_actors(client)
        actor_ids = [a['id'] for a in actors] if actors else []

        print('\n=== Criando filmes ===')
        movies = await create_movies(client, actor_ids)
        movie_ids = [m['id'] for m in movies] if movies else []

        print('\n=== Autenticando usuários ===')
        credentials = [
            ('alice@example.com', 'senha123'),
            ('bruno@example.com', 'senha123'),
            ('carla@example.com', 'senha123'),
        ]
        tokens = []
        for email, password in credentials:
            token = await authenticate(client, email, password)
            if token:
                tokens.append(token)
                print(f'  [+] Login OK: {email}')

        print('\n=== Avaliando filmes ===')
        for token in tokens:
            if movie_ids:
                await rate_movies(client, token, movie_ids)

        print('\n=== Consultando dados ===')
        for _ in range(3):
            await query_data(client)

        print('\n=== Simulando erros 4xx ===')
        await simulate_errors(client)

        print('\n=== Rodada de stress (delay alto) ===')
        for i in range(5):
            await delay(200, 800)
            r = await client.get(f'{BASE}/movies/')
            print(
                f'  [{i + 1}] GET /movies → {r.status_code} | delay simulado'
            )

        print('\n=== Concluído ===')


if __name__ == '__main__':
    start = time.time()
    asyncio.run(main())
    print(f'\nTempo total: {time.time() - start:.2f}s')
