from sqlalchemy.orm import subqueryload

from src.db.uow import AbstractUnitOfWork
from src.models.role import Role
from src.services.base import BaseService


class RoleService(BaseService):
    """Сервис для работы с ролями пользователей"""

    _model = Role
    _model_name = "role"

    def get(self, **query):
        return super().get(
            options=(subqueryload(self._model.permissions),), **query
        )

    def add_permission(self, role_id, service, permission_id):
        role = self.get(id=role_id, convert_to_dict=False)
        permission = service.get(id=permission_id, convert_to_dict=False)
        with self.uow:
            role.permissions.append(permission)

    def remove_permission(self, role_id, service, permission_id):
        role = self.get(id=role_id, convert_to_dict=False)
        permission = service.get(id=permission_id, convert_to_dict=False)
        with self.uow:
            if permission in role.permissions:
                role.permissions.remove(permission)


def get_role_service(uow: AbstractUnitOfWork) -> RoleService:
    return RoleService(uow)
