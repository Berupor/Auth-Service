from src.db.uow import AbstractUnitOfWork
from src.models.social_account import SocialAccount
from src.services.base import BaseService


class SocialAccountService(BaseService):
    """Сервис для работы c аккаунтами социальных сетей"""

    _model = SocialAccount
    _model_name = "social_account"


def get_social_account_service(
    uow: AbstractUnitOfWork,
) -> SocialAccountService:
    return SocialAccountService(uow)
