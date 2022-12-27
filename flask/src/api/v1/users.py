"""API - Пользователи"""

from http import HTTPStatus

from flask import Blueprint, request

from src.api.v1 import schemas
from src.api.v1.decorators import (exception_wrapper, extract_query_parameters,
                                   rate_limit, request_body_validation,
                                   required_permissions)
from src.db.uow import uow
from src.services.login_histories import (LoginHistoryService,
                                          get_login_history_service)
from src.services.roles import RoleService, get_role_service
from src.services.users import UserService, get_user_service


user_routes = Blueprint("user_routes", __name__, url_prefix="/api/v1")


@user_routes.route("/account/", methods=["GET"])
@exception_wrapper("user")
@rate_limit()
@required_permissions([])
def view_account(
    _user_id: int, service: UserService = get_user_service(uow()), **kwargs
) -> tuple[dict, int]:
    model = service.get(id=_user_id)
    return schemas.UserResponse(**model).dict(), HTTPStatus.OK


@user_routes.route("/account/", methods=["PUT"])
@exception_wrapper("user")
@rate_limit()
@required_permissions([])
@request_body_validation()
def update_account(
    _user_id: int, service: UserService = get_user_service(uow()), **kwargs
) -> tuple[dict, int]:
    body = schemas.UserChangeRequest(**request.get_json())
    model = service.update(query={"id": _user_id}, defaults=body.dict())
    return schemas.UserResponse(**model).dict(), HTTPStatus.CREATED


@user_routes.route("/login_history/", methods=["GET"])
@exception_wrapper()
@rate_limit()
@extract_query_parameters(["page[size]", "page[number]"])
@required_permissions([])
def login_history(
    _user_id: int,
    page_num: int,
    page_size: int,
    login_history_service: LoginHistoryService = get_login_history_service(
        uow()
    ),
    **kwargs
) -> tuple[list[dict], int]:
    histories = login_history_service.search(
        _page_num=page_num, _page_size=page_size, user_id=_user_id
    )
    return [
        schemas.LoginHistoryResponse(**x).dict() for x in histories
    ], HTTPStatus.OK


@user_routes.route("/users/<int:user_id>/", methods=["GET"])
@exception_wrapper()
@rate_limit()
@required_permissions(["can_view_user"])
def view_user(
    _user_id: int,
    user_id: int,
    user_service: UserService = get_user_service(uow()),
    **kwargs
) -> tuple[dict, int]:
    user = user_service.get(id=user_id)
    return schemas.UserResponse(**user).dict(), HTTPStatus.OK


@user_routes.route("/users/<int:user_id>/roles/", methods=["POST"])
@exception_wrapper()
@rate_limit()
@required_permissions(["can_add_role_to_user"])
@request_body_validation()
def add_role_to_user(
    _user_id: int,
    user_id: int,
    user_service: UserService = get_user_service(uow()),
    role_service: RoleService = get_role_service(uow()),
    **kwargs
) -> tuple[dict, int]:

    role_id = schemas.AddRoleToUserRequest(**request.get_json()).id
    user_service.add_role(user_id, role_service, role_id)

    user = user_service.get(id=user_id)
    return schemas.UserResponse(**user).dict(), HTTPStatus.CREATED


@user_routes.route(
    "/users/<int:user_id>/roles/<int:role_id>/", methods=["DELETE"]
)
@exception_wrapper()
@rate_limit()
@required_permissions(["can_remove_role_from_user"])
def remove_role_from_user(
    _user_id: int,
    user_id: int,
    role_id: int,
    user_service: UserService = get_user_service(uow()),
    role_service: RoleService = get_role_service(uow()),
    **kwargs
) -> tuple[dict, int]:

    user_service.remove_role(user_id, role_service, role_id)
    user = user_service.get(id=user_id)
    return schemas.UserResponse(**user).dict(), HTTPStatus.NO_CONTENT
