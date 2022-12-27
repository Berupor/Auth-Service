import string
import time
from secrets import choice as secrets_choice

import jwt
from sqlalchemy.orm import subqueryload

from src.api.v1.decorators import trace
from src.core.config import settings
from src.core.exceptions import LoginPasswordWrongException
from src.db.uow import AbstractUnitOfWork
from src.models.base import AbstractModel
from src.models.user import User
from src.services.base import BaseService
from src.services.tools.hasher import PBKDF2PasswordHasher


class UserService(BaseService):
    """Сервис для работы с пользователей"""

    _model = User
    _model_name = "user"
    _hasher = PBKDF2PasswordHasher()

    def get(self, **query) -> dict | AbstractModel:
        return super().get(options=(subqueryload(self._model.roles),), **query)

    @trace()
    def create(
        self,
        login: str,
        password: str,
        email: str,
        first_name: str,
        last_name: str,
        is_superuser: bool = False,
    ) -> dict:

        hashed_password = self._hasher.encode(password, self._hasher.salt())

        return super().create(
            login=login,
            password=hashed_password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_superuser=is_superuser,
        )

    @trace()
    def login(
        self,
        login: str,
        password: str,
    ) -> dict:
        user = self._model.query.filter_by(login=login).first()
        if user and self._hasher.verify(password, user.password):
            return user.to_dict()

        raise LoginPasswordWrongException

    @trace()
    def generate_token_pair(self, user_id: int) -> tuple[str, str, int, int]:
        user = self.get(id=user_id)

        timestamp = round(time.time())
        perms = set()

        for role in user["roles"]:
            for permission in role["permissions"]:
                perms.add(permission["name"])

        base_token = {
            "user_id": user_id,
            #  Минус секунда для компенсации рассинхрона
            #  времени на разных серверах
            "iat": timestamp - 1,
            "permissions": list(perms),
            "is_superuser": user["is_superuser"],
        }

        access_token_expire_at = timestamp + settings.token.access_lifetime
        access_token = {
            **base_token,
            **{
                "exp": access_token_expire_at,
                "token_type": "access",
            },
        }

        refresh_token_expire_at = timestamp + settings.token.refresh_lifetime
        refresh_token = {
            **base_token,
            **{
                "exp": refresh_token_expire_at,
                "token_type": "refresh",
            },
        }

        def encode_token(payload):
            return jwt.encode(
                payload,
                settings.secret_key,
                algorithm=settings.token.algo,
            )

        return (
            encode_token(access_token),
            encode_token(refresh_token),
            access_token_expire_at,
            refresh_token_expire_at,
        )

    def add_role(self, user_id: int, service: BaseService, role_id: int):
        user = self.get(id=user_id, convert_to_dict=False)
        role = service.get(id=role_id, convert_to_dict=False)
        with self.uow:
            user.roles.append(role)

    def remove_role(self, user_id: int, service: BaseService, role_id: int):
        user = self.get(id=user_id, convert_to_dict=False)
        role = service.get(id=role_id, convert_to_dict=False)
        with self.uow:
            if role in user.roles:
                user.roles.remove(role)

    def generate_random_string(self):
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets_choice(alphabet) for _ in range(16))


def get_user_service(uow: AbstractUnitOfWork) -> UserService:
    return UserService(uow)
