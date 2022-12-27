import asyncio
import functools
from functools import wraps

from fastapi import Request, Response, status
from opentelemetry import trace

from src.api.middlewares import get_request_var
from src.core.config import settings
from src.core.http import http_session


tracer = trace.get_tracer(__name__)


async def get_request(request: Request):
    return request


def trace():
    """Трассировка запроса"""

    def inner(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):

            if not settings.enable_tracer:
                return await func(*args, **kwargs)

            request = get_request_var()
            request_id = request.headers.get("X-Request-Id")
            with tracer.start_as_current_span(func.__name__) as span:
                span.set_attribute("http.request_id", request_id)
                return await func(*args, **kwargs)

        return wrapper

    return inner


def auth(permissions: list[str], timeout: int = 1):
    """Проверка разрешений через сервис авторизации"""

    def inner(func):
        @functools.wraps(func)
        async def wrapper(
            *args,
            response: Response,
            **kwargs,
        ):
            request = get_request_var()
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return

            actual_info, degradated_info = await func(
                *args, response, **kwargs
            )

            url = (
                f"http://{settings.flask.host}:{settings.flask.port}"
                "/api/verify_token/"
            )
            data = {"permissions": permissions}
            session = http_session.client(timeout=timeout)

            try:
                headers = {
                    "Authorization": auth_header,
                    "X-Request-Id": request.headers.get("X-Request-Id"),
                }
                async with session.post(
                    url,
                    json=data,
                    headers=headers,
                ) as resp:

                    if resp.status != status.HTTP_200_OK:
                        response.status_code = resp.status
                        return await resp.json()

                    return actual_info

            except asyncio.TimeoutError:
                return degradated_info

        return wrapper

    return inner
