"""API - Роли"""

from http import HTTPStatus

from flask import Blueprint, request

from src.api.v1 import schemas
from src.api.v1.decorators import (exception_wrapper, rate_limit,
                                   request_body_validation,
                                   required_permissions)
from src.db.uow import uow
from src.services.permissions import PermissionService, get_permission_service
from src.services.roles import RoleService, get_role_service


role_routes = Blueprint("role_routes", __name__, url_prefix="/api/v1")


@role_routes.route("/roles/", methods=["GET"])
@exception_wrapper("role")
@rate_limit()
@required_permissions(["can_view_role"])
def get_role(
    _user_id: int, service: RoleService = get_role_service(uow()), **kwargs
) -> tuple[list[dict], int]:
    return [
        schemas.RoleResponse(**x).dict() for x in service.search()
    ], HTTPStatus.OK


@role_routes.route("/roles/", methods=["POST"])
@exception_wrapper("role")
@rate_limit()
@required_permissions(["can_add_role"])
@request_body_validation()
def create_role(
    _user_id: int, service: RoleService = get_role_service(uow()), **kwargs
) -> tuple[dict, int]:
    body = schemas.AddRoleRequest(**request.get_json())
    model = service.create(**body.dict())
    return schemas.RoleResponse(**model).dict(), HTTPStatus.CREATED


@role_routes.route("/roles/<int:role_id>/", methods=["PUT"])
@exception_wrapper("role")
@rate_limit()
@required_permissions(["can_change_role"])
@request_body_validation()
def update_role(
    _user_id: int,
    role_id: int,
    service: RoleService = get_role_service(uow()),
    **kwargs
) -> tuple[dict, int]:
    body = schemas.ChangeRoleRequest(**request.get_json())
    model = service.update(query={"id": role_id}, defaults=body.dict())
    return schemas.RoleResponse(**model).dict(), HTTPStatus.CREATED


@role_routes.route("/roles/<int:role_id>/", methods=["DELETE"])
@exception_wrapper("role")
@rate_limit()
@required_permissions(["can_delete_role"])
def delete_role(
    _user_id: int,
    role_id: int,
    service: RoleService = get_role_service(uow()),
    **kwargs
) -> tuple[dict, int]:
    service.delete(id=role_id)
    return {}, HTTPStatus.NO_CONTENT


@role_routes.route("/roles/<int:role_id>/permissions/", methods=["POST"])
@exception_wrapper()
@rate_limit()
@required_permissions(["can_add_permission_to_role"])
@request_body_validation()
def add_permission_to_role(
    _user_id: int,
    role_id: int,
    role_service: RoleService = get_role_service(uow()),
    permission_service: PermissionService = get_permission_service(uow()),
    **kwargs
) -> tuple[dict, int]:

    permission_id = schemas.AddPermissionToRoleRequest(**request.get_json()).id
    role_service.add_permission(role_id, permission_service, permission_id)

    role = role_service.get(id=role_id)
    return schemas.RoleResponse(**role).dict(), HTTPStatus.CREATED


@role_routes.route(
    "/roles/<int:role_id>/permissions/<int:permission_id>/", methods=["DELETE"]
)
@exception_wrapper()
@rate_limit()
@required_permissions(["can_remove_permission_from_role"])
def remove_permission_from_role(
    _user_id: int,
    role_id: int,
    permission_id: int,
    role_service: RoleService = get_role_service(uow()),
    permission_service: PermissionService = get_permission_service(uow()),
    **kwargs
) -> tuple[dict, int]:
    role_service.remove_permission(role_id, permission_service, permission_id)

    role = role_service.get(id=role_id)
    return schemas.RoleResponse(**role).dict(), HTTPStatus.NO_CONTENT
