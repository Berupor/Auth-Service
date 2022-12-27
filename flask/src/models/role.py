from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from src.db.postgres import Base
from src.models.base import AbstractModel
from src.models.permission import m2m_role_permission_table


m2m_user_role_table = Table(
    "m2m_user_role",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
)


class Role(AbstractModel):
    """БД модель роли"""

    __tablename__ = "roles"

    id = Column(
        Integer,
        primary_key=True,
    )
    name = Column(String, unique=True, nullable=False)

    permissions = relationship(
        "Permission",
        secondary=m2m_role_permission_table,
        back_populates="roles",
    )

    users = relationship(
        "User", secondary=m2m_user_role_table, back_populates="roles"
    )

    def __repr__(self) -> str:
        return f"<Role {self.name}>"

    def to_dict(self) -> dict:
        obj = super().to_dict()
        if self.permissions is not None:
            obj.update(
                {"permissions": [x.to_dict() for x in self.permissions]}
            )

        return obj
