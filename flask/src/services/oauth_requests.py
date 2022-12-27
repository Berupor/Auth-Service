import requests
from pydantic import BaseSettings

from src.core.config import settings
from src.db.uow import AbstractUnitOfWork
from src.models.oauth_request import OAuthRequest
from src.services.base import BaseService


class OAuthRequestService(BaseService):
    """Сервис для работы c запросами OAuth"""

    _model = OAuthRequest
    _model_name = "oauth_request"

    def get_provider_authorization_url(
        self, provider: str, request_id: str
    ) -> str:
        exchangers = {
            "yandex": self._get_yandex_authorization_url,
            "google": self._get_google_authorization_url,
        }

        return exchangers[provider](request_id)

    def _get_yandex_authorization_url(self, request_id: str) -> str:
        scope = settings.oauth.yandex.scope.replace("|", " ")
        return (
            f"{settings.oauth.yandex.authorization_url}?"
            "response_type=code&"
            f"client_id={settings.oauth.yandex.client_id}&"
            f"redirect_uri={settings.url}verification_code&"
            f"scope={scope}&"
            f"state={request_id}"
        )

    def _get_google_authorization_url(self, request_id: str) -> str:
        scope = settings.oauth.google.scope.replace("|", " ")
        return (
            f"{settings.oauth.google.authorization_url}?"
            "response_type=code&"
            f"client_id={settings.oauth.google.client_id}&"
            f"redirect_uri={settings.url}verification_code&"
            f"scope={scope}&"
            f"state={request_id}&"
            "prompt=consent&"
            "include_granted_scopes=true"
        )

    def exchange_code_to_token(self, provider: str, code: str) -> str:
        provider_settings = getattr(settings.oauth, provider)

        exchangers = {
            "yandex": self._exchange_yandex_code_to_token,
            "google": self._exchange_google_code_to_token,
        }

        return exchangers[provider](provider_settings, code)

    def _exchange_yandex_code_to_token(
        self, provider_settings: BaseSettings, code: str
    ) -> str:

        url = settings.oauth.yandex.token_url
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": provider_settings.client_id,
            "client_secret": provider_settings.client_secret,
        }

        response = requests.post(url, data=data, headers=headers)
        json_data = response.json()
        return json_data.get("access_token")

    def _exchange_google_code_to_token(
        self, provider_settings: BaseSettings, code: str
    ) -> str:

        url = settings.oauth.google.token_url
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": provider_settings.client_id,
            "client_secret": provider_settings.client_secret,
            "redirect_uri": f"{settings.url}verification_code",
        }

        response = requests.post(url, data=data, headers=headers)
        json_data = response.json()
        return json_data.get("access_token")

    def exchange_token_to_credentials(self, provider: str, token: str) -> str:
        exchangers = {
            "yandex": self._exchange_yandex_token_to_credentials,
            "google": self._exchange_google_token_to_credentials,
        }

        return exchangers[provider](token)

    def _exchange_yandex_token_to_credentials(self, token: str) -> str:
        url = settings.oauth.yandex.credentials_url
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        json_data = response.json()
        return {
            "social_id": json_data["id"],
            "login": json_data["login"],
            "first_name": json_data["first_name"],
            "last_name": json_data["last_name"],
            "email": json_data["default_email"],
        }

    def _exchange_google_token_to_credentials(self, token: str) -> str:
        url = settings.oauth.google.credentials_url
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        json_data = response.json()
        return {
            "social_id": json_data["id"],
            "login": json_data["email"],
            "first_name": json_data["given_name"],
            "last_name": json_data["family_name"],
            "email": json_data["email"],
        }


def get_oauth_request_service(uow: AbstractUnitOfWork) -> OAuthRequestService:
    return OAuthRequestService(uow)
