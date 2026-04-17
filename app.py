from fastapi import FastAPI, status

from src.routers import users

app = FastAPI()

app.include_router(prefix='/api/v1/users', tags=['users'], router=users.router)


@app.get('/health', status_code=status.HTTP_200_OK)
async def health_check():
    return {'message': 'Hello World'}
