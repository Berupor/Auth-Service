from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from src.db.postgres import Base
from src.models.base import AbstractModel


m2m_role_permission_table = Table(
    "m2m_role_permission",
    Base.metadata,
    Column("permission_id", ForeignKey("permissions.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
)


class Permission(AbstractModel):
    """БД модель разрешения"""

    __tablename__ = "permissions"

    id = Column(
        Integer,
        primary_key=True,
    )
    name = Column(String, unique=True, nullable=False)

    roles = relationship(
        "Role",
        secondary=m2m_role_permission_table,
        back_populates="permissions",
    )

    def __repr__(self) -> str:
        return f"<Permission {self.name}>"
