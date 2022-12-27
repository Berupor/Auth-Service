import time

from sqlalchemy.orm import subqueryload

from src.db.cache import cache
from src.db.uow import AbstractUnitOfWork
from src.models.login_history import LoginHistory
from src.services.base import BaseService


class LoginHistoryService(BaseService):
    """Сервис для работы историями входов"""

    _model = LoginHistory
    _order_by = (_model.logged_at.desc(),)
    _model_name = "login_histories"

    def search(self, **query):
        return super().search(
            options=(subqueryload(self._model.device),), **query
        )

    def dispose_token_pair(self, **query):
        timestamp = round(time.time())
        models = self.search(
            convert_to_dict=False,
            **{**query, **{"refresh_token_expire_at__gt": timestamp}}
        )
        for model in models:
            cache.set(
                model.access_token,
                1,
                expire_at=model.access_token_expire_at,
            )
            cache.set(
                model.refresh_token,
                1,
                expire_at=model.refresh_token_expire_at,
            )


def get_login_history_service(uow: AbstractUnitOfWork) -> LoginHistoryService:
    return LoginHistoryService(uow)
