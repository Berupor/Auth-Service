"""Команды CLI для работы с пользователями"""

from flask import Blueprint, current_app

from src.core import exceptions
from src.core.config import settings
from src.db.uow import uow
from src.services.users import UserService, get_user_service


user_commands = Blueprint("users", __name__)


@user_commands.cli.command("createsuperuser")
def create_super_user(
    service: UserService = get_user_service(uow()),
):
    try:
        service.create(
            login=settings.superuser.username,
            password=settings.superuser.password,
            email=settings.superuser.email,
            first_name="",
            last_name="",
            is_superuser=True,
        )
        current_app.logger.warning(
            "Super user '%s' is created", settings.superuser.username
        )

    except exceptions.NotUniqueDbException:
        current_app.logger.error("Super user has been already created before")
