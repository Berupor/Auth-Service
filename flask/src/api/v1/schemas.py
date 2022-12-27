"""API - Модели валидации запросов и формировани ответов"""

from datetime import datetime

from pydantic import BaseModel, Field, PositiveInt, root_validator, validator

from src.core.config import settings


class IdMixin(BaseModel):
    id: int


class NameMixin(BaseModel):
    name: str


class VerifyTokenRequest(BaseModel):
    """Модель запроса проверки разрешений"""

    permissions: list[str]


class RegisterRequest(BaseModel):
    """Модель запроса на регистрацию"""

    login: str
    password: str = Field(..., min_length=3)
    email: str
    first_name: str
    last_name: str


class LoginRequest(BaseModel):
    """Модель запроса на вход"""

    login: str
    password: str


class UserChangeRequest(BaseModel):
    """Модель запроса на изменение данных пользователя"""

    login: str = None
    password: str = Field(None, min_length=3)
    email: str = None
    first_name: str = None
    last_name: str = None

    @root_validator
    def any_of(cls, v):
        if not any(v.values()):
            raise ValueError(
                "at least one of login, password, email,"
                " first_name, last_name must have a value"
            )
        return v

    def dict(self):
        return super().dict(exclude_none=True)


class AddPermissionRequest(NameMixin):
    """Модель запроса на добавление разрешения"""

    pass


class ChangePermissionRequest(NameMixin):
    """Модель запроса на изменение разрешения"""

    pass


class AddPermissionToRoleRequest(IdMixin):
    """Модель запроса на добавление разрешения к роли"""

    pass


class AddRoleRequest(NameMixin):
    """Модель запроса на добавление роли"""

    pass


class ChangeRoleRequest(NameMixin):
    """Модель запроса на изменение роли"""

    pass


class AddRoleToUserRequest(IdMixin):
    """Модель запроса на добавление роли к пользователю"""

    pass


class ChangeDeviceRequest(BaseModel):
    """Модель запроса на изменение устройства пользователя"""

    is_allowed: bool


class RoleWithoutPermissionsResponse(IdMixin, NameMixin):
    """Модель ответа роли без разрешений"""

    pass


class PermissionResponse(IdMixin, NameMixin):
    """Модель ответа разрешения пользователя"""

    def __hash__(self) -> int:
        return self.id


class RoleResponse(RoleWithoutPermissionsResponse):
    """Модель ответа роли с разрешениями"""

    permissions: list[PermissionResponse]


class DeviceResponse(IdMixin):
    """Модель ответа устройства пользователя"""

    fingerprint: str
    is_allowed: bool


class UserResponse(IdMixin):
    """Модель ответа пользователя"""

    login: str
    email: str
    first_name: str
    last_name: str
    roles: list[RoleResponse]

    def dict(self):
        roles = []
        perms = set()
        obj = dict(self)

        for role in obj["roles"]:
            roles.append(role.dict(include={"id", "name"}))
            perms.update(role.permissions)

        obj["roles"] = roles
        obj["permissions"] = [x.dict() for x in list(perms)]

        return obj


class LoginHistoryResponse(BaseModel):
    """Модель ответа истории входа пользователя"""

    device: DeviceResponse
    logged_at: datetime


class PageNumberQueryParamSchema(BaseModel):
    """Модель параметра номера страницы"""

    page_num: PositiveInt = Field(1, alias="page[number]")


class PageSizeQueryParamSchema(BaseModel):
    """Модель параметра количества записей на странице"""

    page_size: PositiveInt = Field(settings.page_size, alias="page[size]")

    @validator("page_size")
    def must_be_less_than_thousand(cls, v):
        if v > 1000:
            raise ValueError("must be <= 1000")
        return v


class OAuthStateQueryParamSchema(BaseModel):
    """Модель параметра состояния запроса OAuth"""

    state: str


class OAuthCodeQueryParamSchema(BaseModel):
    """Модель параметра кода ответа запроса OAuth"""

    code: str
