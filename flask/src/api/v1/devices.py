"""API - Устройства пользователей"""

from http import HTTPStatus

from flask import Blueprint, request

from src.api.v1 import schemas
from src.api.v1.decorators import (exception_wrapper, rate_limit,
                                   request_body_validation,
                                   required_permissions)
from src.db.uow import uow
from src.services.devices import DeviceService, get_device_service
from src.services.login_histories import (LoginHistoryService,
                                          get_login_history_service)


device_routes = Blueprint("device_routes", __name__, url_prefix="/api/v1")


@device_routes.route("/devices/<int:device_id>/", methods=["PUT"])
@exception_wrapper("device")
@rate_limit()
@required_permissions(["can_change_device"])
@request_body_validation()
def update_permission(
    _user_id,
    device_id,
    device_service: DeviceService = get_device_service(uow()),
    login_history_service: LoginHistoryService = get_login_history_service(
        uow()
    ),
    **kwargs
) -> tuple[dict, int]:

    body = schemas.ChangeDeviceRequest(**request.get_json())
    if not body.is_allowed:
        login_history_service.dispose_token_pair(device_id=device_id)

    model = device_service.update(
        query={"id": device_id},
        defaults=body.dict(),
    )
    return schemas.DeviceResponse(**model).dict(), HTTPStatus.CREATED
