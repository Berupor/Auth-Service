"""API - Разрешения пользователей"""

from http import HTTPStatus

from flask import Blueprint, request

from src.api.v1 import schemas
from src.api.v1.decorators import (exception_wrapper, rate_limit,
                                   request_body_validation,
                                   required_permissions)
from src.db.uow import uow
from src.services.permissions import PermissionService, get_permission_service


permission_routes = Blueprint(
    "permission_routes", __name__, url_prefix="/api/v1"
)


@permission_routes.route("/permissions/", methods=["GET"])
@exception_wrapper("permission")
@rate_limit()
@required_permissions(["can_view_permission"])
def get_permission(
    _user_id: int,
    service: PermissionService = get_permission_service(uow()),
    **kwargs
) -> tuple[list[dict], int]:
    return [
        schemas.PermissionResponse(**x).dict() for x in service.search()
    ], HTTPStatus.OK


@permission_routes.route("/permissions/", methods=["POST"])
@exception_wrapper("permission")
@rate_limit()
@required_permissions(["can_add_permission"])
@request_body_validation()
def create_permission(
    _user_id: int,
    service: PermissionService = get_permission_service(uow()),
    **kwargs
) -> tuple[dict, int]:
    body = schemas.AddPermissionRequest(**request.get_json())
    model = service.create(**body.dict())
    return schemas.PermissionResponse(**model).dict(), HTTPStatus.CREATED


@permission_routes.route("/permissions/<int:permission_id>/", methods=["PUT"])
@exception_wrapper("permission")
@rate_limit()
@required_permissions(["can_change_permission"])
@request_body_validation()
def update_permission(
    _user_id: int,
    permission_id: int,
    service: PermissionService = get_permission_service(uow()),
    **kwargs
) -> tuple[dict, int]:
    body = schemas.ChangePermissionRequest(**request.get_json())
    model = service.update(query={"id": permission_id}, defaults=body.dict())
    return schemas.PermissionResponse(**model).dict(), HTTPStatus.CREATED


@permission_routes.route(
    "/permissions/<int:permission_id>/", methods=["DELETE"]
)
@exception_wrapper("permission")
@rate_limit()
@required_permissions(["can_delete_permission"])
def delete_permission(
    _user_id: int,
    permission_id: int,
    service: PermissionService = get_permission_service(uow()),
    **kwargs
) -> tuple[dict, int]:
    service.delete(id=permission_id)
    return {}, HTTPStatus.NO_CONTENT
