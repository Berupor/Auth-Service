"""API - Авторизация"""

from http import HTTPStatus

from flask import Blueprint, request

from src.api.v1 import schemas
from src.api.v1.decorators import (exception_wrapper, rate_limit,
                                   request_body_validation,
                                   required_permissions, trace)
from src.core import exceptions
from src.db.uow import uow
from src.services.devices import DeviceService, get_device_service
from src.services.login_histories import (LoginHistoryService,
                                          get_login_history_service)
from src.services.users import UserService, get_user_service


auth_routes = Blueprint("auth_routes", __name__, url_prefix="/api")


@auth_routes.route("/register/", methods=["POST"])
@exception_wrapper("user")
@rate_limit()
@request_body_validation()
def register(
    service: UserService = get_user_service(uow()), **kwargs
) -> tuple[dict, int]:

    body = schemas.RegisterRequest(**request.get_json())
    model = service.create(**body.dict())
    return schemas.UserResponse(**model).dict(), HTTPStatus.CREATED


def login_by_user(
    user_id: int,
    user_service: UserService = get_user_service(uow()),
    device_service: DeviceService = get_device_service(uow()),
    login_history_service: LoginHistoryService = get_login_history_service(
        uow()
    ),
) -> tuple[str, str]:

    #  Получаем устройство, с которого произведен вход
    fingerprint = request.user_agent.string
    device, _ = device_service.get_or_create_allowed_device(
        user_id, fingerprint
    )
    device_id = device["id"]

    device_type = device_service.get_device_type(fingerprint)
    login_history_service.dispose_token_pair(device_id=device_id)

    #  Генерируем новые токены
    (
        access_token,
        refresh_token,
        access_token_expire_at,
        refresh_token_expire_at,
    ) = user_service.generate_token_pair(user_id)

    #  Обновляем запись в истории новыми токенами
    login_history_service.create(
        user_id=user_id,
        device_id=device_id,
        device_type=device_type,
        access_token=access_token,
        refresh_token=refresh_token,
        access_token_expire_at=access_token_expire_at,
        refresh_token_expire_at=refresh_token_expire_at,
    )

    return access_token, refresh_token


@auth_routes.route("/login/", methods=["POST"])
@exception_wrapper("login history")
@rate_limit()
@trace()
@request_body_validation()
def login(
    user_service: UserService = get_user_service(uow()), **kwargs
) -> tuple[dict, int]:

    body = schemas.LoginRequest(**request.get_json())
    user = user_service.login(**body.dict())
    access_token, refresh_token = login_by_user(user["id"])

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }, HTTPStatus.OK


@auth_routes.route("/logout/", methods=["POST"])
@exception_wrapper()
@rate_limit()
@required_permissions([])
def logout(
    _user_id,
    device_service: DeviceService = get_device_service(uow()),
    login_history_service: LoginHistoryService = get_login_history_service(
        uow()
    ),
    **kwargs
) -> tuple[dict, int]:
    device = device_service.get(
        user_id=_user_id, fingerprint=request.user_agent.string
    )
    login_history_service.dispose_token_pair(device_id=device["id"])

    return {}, HTTPStatus.NO_CONTENT


@auth_routes.route("/logout/all/", methods=["POST"])
@exception_wrapper()
@rate_limit()
@required_permissions([])
def logout_on_all_devices(
    _user_id,
    login_history_service: LoginHistoryService = get_login_history_service(
        uow()
    ),
    **kwargs
) -> tuple[dict, int]:
    login_history_service.dispose_token_pair(user_id=_user_id)
    return {}, HTTPStatus.NO_CONTENT


@auth_routes.route("/refresh/", methods=["GET"])
@exception_wrapper()
@rate_limit()
@required_permissions([], False)
def refresh(
    _user_id,
    _token,
    user_service: UserService = get_user_service(uow()),
    login_history_service: LoginHistoryService = get_login_history_service(
        uow()
    ),
    **kwargs
) -> tuple[dict, int]:

    #  Сбрасываем токены от данного устройства
    login_history_service.dispose_token_pair(refresh_token=_token)

    #  Генерируем новые токены
    (
        access_token,
        refresh_token,
        access_token_expire_at,
        refresh_token_expire_at,
    ) = user_service.generate_token_pair(_user_id)

    #  Обновляем запись в истории новыми токенами
    login_history_service.update_or_create(
        query={"refresh_token": _token},
        defaults={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "access_token_expire_at": access_token_expire_at,
            "refresh_token_expire_at": refresh_token_expire_at,
        },
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }, HTTPStatus.OK


@auth_routes.route("/verify_token/", methods=["POST"])
@exception_wrapper()
@rate_limit()
@required_permissions([])
@request_body_validation()
def verify_token(
    _is_superuser: bool, _token_permissions: list[str], **kwargs
) -> tuple[dict, int]:

    required_permissions = schemas.VerifyTokenRequest(
        **request.get_json()
    ).permissions

    if (
        not _is_superuser
        and len(set(required_permissions) - set(_token_permissions)) > 0
    ):
        raise exceptions.NoPermissionException

    return {}, HTTPStatus.OK
