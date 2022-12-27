from src.db.postgres import Base


class AbstractModel(Base):
    """Базовая БД модель"""

    __abstract__ = True

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
