from src.api.v1.decorators import trace
from src.core import exceptions
from src.db.postgres import db_session
from src.db.uow import AbstractUnitOfWork
from src.models.base import AbstractModel


class BaseService:
    """Базовый сервис"""

    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    def _convert_query_to_filter(self, query: dict) -> tuple:
        endings = {
            "gt": "__gt__",
            "lt": "__lt__",
            "ge": "__ge__",
            "le": "__le__",
        }

        def convert_key(key: str) -> str:
            parts = key.split("__")
            if len(parts) == 1:
                return key, "__eq__"

            last = parts.pop()
            operator = endings[last] if last and last in endings else "__eq__"
            return "__".join(parts), operator

        filters = []
        for k, v in query.items():
            field_name, operator = convert_key(k)
            field = getattr(self._model, field_name)
            filter_func = getattr(field, operator)
            filters.append(filter_func(v))

        return filters

    @trace()
    def create(self, **attrs) -> dict:
        with self.uow:
            model = self._model(**attrs)
            db_session.add(model)

        return model.to_dict()

    @trace()
    def get(
        self, options: tuple = (), convert_to_dict: bool = True, **query
    ) -> AbstractModel | dict:
        filters = self._convert_query_to_filter(query)
        with self.uow:
            model = (
                self._model.query.filter(*filters).options(*options).first()
            )

        if not model:
            raise exceptions.ModelNotFoundException(self._model_name)

        return model.to_dict() if convert_to_dict else model

    @trace()
    def search(
        self,
        options: tuple = (),
        convert_to_dict: bool = True,
        _page_num: int | None = None,
        _page_size: int | None = None,
        **query
    ) -> list[AbstractModel | dict]:

        filters = self._convert_query_to_filter(query)

        with self.uow:
            db_query = self._model.query.filter(*filters).options(*options)

            if hasattr(self, "_order_by"):
                db_query = db_query.order_by(*self._order_by)

            if _page_num and _page_size:
                db_query = db_query.limit(_page_size).offset(
                    _page_size * (_page_num - 1)
                )

            return [
                (x.to_dict() if convert_to_dict else x) for x in db_query.all()
            ]

    @trace()
    def update(self, query: dict, defaults: dict = {}) -> dict:
        filters = self._convert_query_to_filter(query)
        model = self._model.query.filter(*filters).first()
        if not model:
            raise exceptions.ModelNotFoundException(self._model_name)

        with self.uow:
            for k, v in defaults.items():
                if k == "password":
                    v = self._hasher.encode(v, self._hasher.salt())
                setattr(model, k, v)

        return model.to_dict()

    @trace()
    def get_or_create(
        self, query: dict, defaults: dict = {}
    ) -> tuple[dict, bool]:
        created = False
        filters = self._convert_query_to_filter(query)

        with self.uow:
            model = self._model.query.filter(*filters).first()
            if not model:
                model = self._model(**{**query, **defaults})
                db_session.add(model)
                created = True

        return model.to_dict(), created

    @trace()
    def update_or_create(
        self, query: dict, defaults: dict = {}
    ) -> tuple[dict, bool]:
        filters = self._convert_query_to_filter(query)

        with self.uow:
            model = self._model.query.filter(*filters).first()

            if model:
                updated_model = self.update(
                    query={"id": model.id}, defaults=defaults
                )
                return updated_model, False

            new_values = query
            new_values.update(defaults)
            model = self._model(**new_values)
            db_session.add(model)

        return model.to_dict(), True

    @trace()
    def delete(self, **query):
        with self.uow:
            filters = self._convert_query_to_filter(query)
            self._model.query.filter(*filters).delete()
