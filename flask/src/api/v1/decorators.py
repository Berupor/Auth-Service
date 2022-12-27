"""Декораторы"""

import datetime
from functools import wraps
from http import HTTPStatus

import jwt
import pydantic
from flask import request
from opentelemetry import trace

from src.api.v1 import schemas
from src.core import exceptions
from src.core.config import settings
from src.db.cache import cache
from src.db.postgres import db_session


tracer = trace.get_tracer(__name__)


def trace():
    """Трассировка запроса"""

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):

            if not settings.enable_tracer:
                return func(*args, **kwargs)

            request_id = request.headers.get("X-Request-Id")
            with tracer.start_as_current_span(func.__name__) as span:
                span.set_attribute("http.request_id", request_id)
                return func(*args, **kwargs)

        return inner

    return func_wrapper


def exception_wrapper(model_name: str = ""):
    """Обработка исключений приложения"""

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result

            except exceptions.DbException as e:
                message = e.message

                if isinstance(e, exceptions.NotUniqueDbException):
                    message = (
                        f"{model_name.capitalize()} with "
                        f"same '{e.field}' field is already exist"
                    )

                if isinstance(e, exceptions.NotNullDbException):
                    message = f"Not null violation of '{e.field}' field"

                return {
                    "error": e.code,
                    "message": message,
                }, HTTPStatus.BAD_REQUEST

            except exceptions.BadRequestException as e:
                return {
                    "error": e.code,
                    "message": f"{e.message}: {e.field}",
                }, HTTPStatus.BAD_REQUEST

            except exceptions.TooManyRequests as e:
                return {
                    "error": e.code,
                    "message": e.message,
                }, HTTPStatus.TOO_MANY_REQUESTS

            except exceptions.ModelNotFoundException as e:
                return {
                    "error": e.code,
                    "message": f"{e.field.capitalize()} not found",
                }, HTTPStatus.FORBIDDEN

            except (
                exceptions.LoginPasswordWrongException,
                exceptions.AuthTokenMissedException,
                exceptions.AuthTokenOutdatedException,
                exceptions.AuthTokenWithWrongSignatureException,
                exceptions.AuthTokenWrongPayloadException,
            ) as e:
                return {
                    "error": e.code,
                    "message": e.message,
                }, HTTPStatus.UNAUTHORIZED

            except exceptions.NoPermissionException as e:
                return {
                    "error": e.code,
                    "message": e.message,
                }, HTTPStatus.FORBIDDEN

            finally:
                db_session.close()

        return inner

    return func_wrapper


def request_body_validation():
    """Валидация тела запроса"""

    def func_wrapper(func):
        @trace()
        @wraps(func)
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)

            except pydantic.error_wrappers.ValidationError as e:
                error = e.errors()[0]
                raise exceptions.BadRequestException(
                    error["msg"], ", ".join(error["loc"])
                )

        return inner

    return func_wrapper


def required_permissions(
    required_permissions: list[str],
    is_access_token: bool = True,
):
    """Проверка требуемых разрешений"""

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise exceptions.AuthTokenMissedException

            parts = auth_header.split()

            if len(parts) != 2 or parts[0] != "Bearer":
                raise exceptions.AuthTokenMissedException

            encoded_token = parts[1]

            try:
                payload = jwt.decode(
                    encoded_token, settings.secret_key, [settings.token.algo]
                )

            except (
                jwt.exceptions.InvalidSignatureError,
                jwt.exceptions.DecodeError,
            ):
                raise exceptions.AuthTokenWithWrongSignatureException

            except jwt.exceptions.ExpiredSignatureError:
                raise exceptions.AuthTokenOutdatedException

            if cache.get(encoded_token):
                raise exceptions.AuthTokenOutdatedException

            token_permissions = payload.get("permissions")
            user_id = payload.get("user_id")
            token_type = payload.get("token_type")
            is_superuser = payload.get("is_superuser")

            if (
                token_permissions is None
                or user_id is None
                or is_superuser is None
                or token_type is None
                or (token_type == "access") != is_access_token  # noqa: S105
            ):
                raise exceptions.AuthTokenWrongPayloadException

            if (
                not is_superuser
                and len(set(required_permissions) - set(token_permissions)) > 0
            ):
                raise exceptions.NoPermissionException

            additional_kwargs = {
                "_user_id": user_id,
                "_is_superuser": is_superuser,
                "_token_permissions": token_permissions,
            }

            if token_type == "refresh":  # noqa: S105
                additional_kwargs.update({"_token": encoded_token})

            return func(*args, **kwargs, **additional_kwargs)

        return inner

    return func_wrapper


def extract_query_parameters(
    params: list[str],
):
    """Извлечение параметров из строки запроса"""

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):

            validation_schemas = {
                "state": schemas.OAuthStateQueryParamSchema,
                "code": schemas.OAuthCodeQueryParamSchema,
                "page[number]": schemas.PageNumberQueryParamSchema,
                "page[size]": schemas.PageSizeQueryParamSchema,
            }

            additional_kwargs = {}
            for key in params:
                value = request.args.get(key)
                try:
                    kwargs = {} if value is None else {key: value}
                    model = validation_schemas[key](**kwargs)
                    additional_kwargs.update(model.dict())

                except pydantic.error_wrappers.ValidationError as e:
                    error = e.errors()[0]
                    raise exceptions.BadRequestException(
                        error["msg"], ", ".join(error["loc"])
                    )

            kwargs.update(additional_kwargs)
            return func(*args, **kwargs)

        return inner

    return func_wrapper


def rate_limit(limit=30):
    """Ограничение количества запросов к серверу"""

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):

            now = datetime.datetime.now()
            ip = request.remote_addr

            if cache.count_rate_limit(f"{ip}:{now.minute}", limit):
                return func(*args, **kwargs)

            raise exceptions.TooManyRequests

        return inner

    return func_wrapper
