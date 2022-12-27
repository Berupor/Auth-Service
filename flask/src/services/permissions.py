from src.db.uow import AbstractUnitOfWork
from src.models.permission import Permission
from src.services.base import BaseService


class PermissionService(BaseService):
    """Сервис для работы c разрешениями пользователей"""

    _model = Permission
    _model_name = "permission"


def get_permission_service(uow: AbstractUnitOfWork) -> PermissionService:
    return PermissionService(uow)
