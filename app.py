from fastapi import FastAPI, status

from src.routers import actors, auth, movies, users

app = FastAPI()

app.include_router(prefix='/api/v1/auth', tags=['auth'], router=auth.router)

app.include_router(prefix='/api/v1/users', tags=['users'], router=users.router)

app.include_router(
    prefix='/api/v1/movies', tags=['movies'], router=movies.router
)

app.include_router(
    prefix='/api/v1/actors', tags=['actors'], router=actors.router
)


@app.get('/health', status_code=status.HTTP_200_OK)
async def health_check():
    return {'message': 'Hello World'}
