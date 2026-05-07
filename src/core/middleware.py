import time
import typing

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from src.core.metrics import http_request, http_request_duration


class Middleware(BaseHTTPMiddleware):
    @typing.override
    async def dispatch(self, request: Request, call_next):
        start = time.time()

        response = await call_next(request)

        http_request.add(
            1,
            {
                'method': request.method,
                'endpoint': request.url.path,
                'status_code': response.status_code,
            },
        )
        end = time.time()

        http_request_duration.record(
            end - start,
            {
                'method': request.method,
                'endpoint': request.url.path,
                'status_code': response.status_code,
            },
        )

        return response
