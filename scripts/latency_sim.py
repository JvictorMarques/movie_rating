import asyncio
import random
import time

import httpx

BASE = 'http://localhost:8000/api/v1'

ENDPOINTS = [
    ('GET', '/movies/'),
    ('GET', '/users/'),
    ('GET', '/actors/'),
    ('GET', '/movies/1'),
    ('GET', '/movies/2'),
    ('GET', '/movies/3'),
    ('GET', '/movies/99999'),  # 404
]


async def request(
    client: httpx.AsyncClient, method: str, path: str, delay_ms: int
) -> None:
    await asyncio.sleep(delay_ms / 1000)
    url = f'{BASE}{path}'
    r = await client.request(method, url)
    print(f'  [{delay_ms:>4}ms delay] {method} {path} → {r.status_code}')


async def burst(
    client: httpx.AsyncClient, label: str, min_ms: int, max_ms: int, count: int
) -> None:
    print(f'\n--- {label} ({min_ms}–{max_ms}ms) ---')
    tasks = [
        request(client, method, path, random.randint(min_ms, max_ms))
        for method, path in random.choices(ENDPOINTS, k=count)
    ]
    await asyncio.gather(*tasks)


async def main() -> None:
    async with httpx.AsyncClient(timeout=30) as client:
        print('=== Simulação de latência ===\n')

        # requisições rápidas
        await burst(client, 'Rápidas', 5, 50, 10)

        # latência média
        await burst(client, 'Médias', 100, 300, 10)

        # picos lentos (cauda do p99)
        await burst(client, 'Lentas', 500, 1500, 5)

        # mix realista
        await burst(client, 'Mix realista', 10, 800, 20)

        print('\n=== Concluído ===')


if __name__ == '__main__':
    start = time.time()
    asyncio.run(main())
    print(f'Tempo total: {time.time() - start:.2f}s')
