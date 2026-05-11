import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.core.database import engine
from src.core.middleware import Middleware
from src.core.settings import Settings
from src.core.telemetry import setup_telemetry
from src.routers import actors, auth, movies, users

app = FastAPI()
settings = Settings()
logger = logging.getLogger(__name__)

if settings.OTLP_ENDPOINT:
    setup_telemetry(app, engine)

app.add_middleware(Middleware)

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


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        'Unhandled exception',
        extra={
            'method': request.method,
            'path': request.url.path,
            'error': str(exc),
        },
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'detail': 'Internal Server Error'},
    )
