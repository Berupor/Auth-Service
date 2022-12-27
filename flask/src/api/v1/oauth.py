"""API - Авторизация"""

import uuid
from enum import Enum
from http import HTTPStatus

from flask import Blueprint, abort, current_app, redirect, request

from src.api.v1 import schemas
from src.api.v1.auth import login_by_user
from src.api.v1.decorators import (exception_wrapper, extract_query_parameters,
                                   rate_limit)
from src.core import exceptions
from src.db.uow import uow
from src.services.oauth_requests import (OAuthRequestService,
                                         get_oauth_request_service)
from src.services.social_accounts import (SocialAccountService,
                                          get_social_account_service)
from src.services.users import UserService, get_user_service


oauth_routes = Blueprint("oauth_routes", __name__, url_prefix="/api")


class Providers(str, Enum):
    YANDEX = "yandex"
    GOOGLE = "google"


@oauth_routes.route("/login/<string:provider>/", methods=["GET"])
@exception_wrapper("oauth_request")
@rate_limit()
def register(
    provider: str,
    oauth_request_service: OAuthRequestService = get_oauth_request_service(
        uow()
    ),
    **kwargs
):
    if provider not in Providers._value2member_map_:
        abort(HTTPStatus.NOT_FOUND)

    request_id = uuid.uuid4()

    oauth_request_service.create(
        id=request_id,
        provider=provider,
        fingerprint=request.user_agent.string,
    )

    url = oauth_request_service.get_provider_authorization_url(
        provider, request_id
    )
    return redirect(url, code=HTTPStatus.TEMPORARY_REDIRECT)


@oauth_routes.route("/verification_code/", methods=["GET"])
@exception_wrapper("oauth_request")
@rate_limit()
@extract_query_parameters(["state", "code"])
def verification_code(
    state: str,
    code: str,
    user_service: UserService = get_user_service(uow()),
    social_account_service: SocialAccountService = get_social_account_service(
        uow()
    ),
    oauth_request_service: OAuthRequestService = get_oauth_request_service(
        uow()
    ),
    **kwargs
):
    try:
        oauth_request = oauth_request_service.get(id=state)
        access_token = oauth_request_service.exchange_code_to_token(
            oauth_request["provider"], code
        )
    except exceptions.ApiException as e:
        current_app.logger.error(str(e))
        raise exceptions.BadRequestException(
            "Query parameter 'state' is wrong"
        )

    if not access_token:
        raise exceptions.LoginPasswordWrongException

    credentials = oauth_request_service.exchange_token_to_credentials(
        oauth_request["provider"], access_token
    )

    #  Проверяем существует ли такой SocialAccount
    accounts = social_account_service.search(
        social_id=credentials["social_id"]
    )

    #  Если да, извлекаем аккаунт соц сети и пользователя
    if accounts:
        account = accounts[0]

    else:
        #  Если нет, создаем нового пользователя
        credentials.update({"password": user_service.generate_random_string()})
        data_for_registration = schemas.RegisterRequest(**credentials)
        user = user_service.create(**data_for_registration.dict())

        #  Создаем новый аккаунт социальной сети
        account = social_account_service.create(
            user_id=user["id"],
            social_id=credentials["social_id"],
            provider=oauth_request["provider"],
        )

    access_token, refresh_token = login_by_user(account["user_id"])

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }, HTTPStatus.OK
