from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from src.models.base import AbstractModel
from src.models.role import m2m_user_role_table


class User(AbstractModel):
    """БД модель пользователя"""

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
    )
    login = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String, default="", nullable=False)
    last_name = Column(String, default="", nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    roles = relationship(
        "Role",
        secondary=m2m_user_role_table,
        back_populates="users",
        lazy="subquery",
    )

    social_accounts = relationship(
        "SocialAccount",
        back_populates="user",
        lazy="subquery",
        cascade="all, delete",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<User {self.login}>"

    def to_dict(self) -> dict:
        obj = super().to_dict()
        if self.roles is not None:
            obj.update({"roles": [x.to_dict() for x in self.roles]})

        return obj
