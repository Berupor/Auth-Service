"""Модуль исключений приложения"""

from dataclasses import dataclass


class ApiException(Exception):
    pass


class AuthTokenMissedException(ApiException):
    message: str = "Bearer token has not been provided"
    code: str = "A001"


class AuthTokenOutdatedException(ApiException):
    message: str = "Token is outdated"
    code: str = "A002"


class AuthTokenWithWrongSignatureException(ApiException):
    message: str = "Token with wrong signature"
    code: str = "A003"


class LoginPasswordWrongException(ApiException):
    message: str = "Pair of login and password is not correct"
    code: str = "A004"


class NoPermissionException(ApiException):
    message: str = "Operation is not permitted"
    code: str = "A005"


class AuthTokenWrongPayloadException(ApiException):
    message: str = "Token with wrong payload"
    code: str = "A006"


class OAuthRegistrationException(ApiException):
    message: str = "Error during authentication through social provider"
    code: str = "A007"


@dataclass
class BadRequestException(ApiException):
    message: str
    field: str | None = None
    code: str = "B001"


@dataclass
class DbException(ApiException):
    message: str
    field: str | None = None
    code: str = "B001"


@dataclass
class NotUniqueDbException(DbException):
    code: str = "B002"


class NotNullDbException(DbException):
    pass


@dataclass
class ModelNotFoundException(ApiException):
    field: str
    code: str = "B003"


class TooManyRequests(ApiException):
    message: str = "Too Many Requests"
    code: str = "C001"
