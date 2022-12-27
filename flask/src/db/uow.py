import abc
import re

import sqlalchemy

from src.core import exceptions
from src.db.postgres import db_session


class AbstractUnitOfWork(abc.ABC):
    """Абстрактный класс для работы с сессиями БД"""

    def __enter__(self):
        return self

    @abc.abstractmethod
    def __exit__(self, *args):
        raise NotImplementedError


class FlaskUnitOfWork(AbstractUnitOfWork):
    """SQLAlchemy класс для работы с сессиями БД"""

    def __enter__(self):
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        if (
            exc_type
            and exc_value
            and issubclass(exc_type, sqlalchemy.exc.DBAPIError)
        ):
            message = self.parse_error_detail(str(exc_value))
            raise exceptions.DbException(message)

        try:
            db_session.commit()

        except sqlalchemy.exc.DBAPIError as e:
            db_session.rollback()
            message = self.parse_error_detail(str(e))

            if isinstance(e, sqlalchemy.exc.IntegrityError):

                if "UniqueViolation" in str(e):
                    field = self.parse_field_name(
                        r"Key \((?P<field>[\w\s,]+)\)=", str(e)
                    )
                    raise exceptions.NotUniqueDbException(message, field)

                if "NotNullViolation" in str(e):
                    field = self.parse_field_name(
                        r'column "(?P<field>\w+)" of', str(e)
                    )
                    raise exceptions.NotNullDbException(message, field)

            raise exceptions.DbException(message)

    def parse_error_detail(self, text: str) -> str:
        if matches := re.search(r"DETAIL:(?P<detail>.*)$", text, flags=re.M):
            if detail := matches.group("detail"):
                return detail.strip()
        return "DB Error"

    def parse_field_name(self, regex: str, text: str) -> str:
        matches = re.search(regex, text)
        return matches.group("field") if matches else "unknown field"


def uow() -> AbstractUnitOfWork:
    return FlaskUnitOfWork()
