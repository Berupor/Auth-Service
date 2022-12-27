import uuid

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String,
                        UniqueConstraint)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.models.base import AbstractModel


def create_partition(target, connection, **kw) -> None:
    """Создание партиций историй входа пользователя"""

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS "login_histories_smart"
         PARTITION OF "login_histories" FOR VALUES IN ('smart');
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS "login_histories_mobile"
         PARTITION OF "login_histories" FOR VALUES IN ('mobile');
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS "login_histories_web"
         PARTITION OF "login_histories" FOR VALUES IN ('web')
        """
    )


class LoginHistory(AbstractModel):
    """БД модель истории входа пользователя"""

    __tablename__ = "login_histories"
    __table_args__ = (
        UniqueConstraint("id", "device_type"),
        {
            "postgresql_partition_by": "LIST (device_type)",
            "listeners": [("after_create", create_partition)],
        },
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    device_type = Column(String, primary_key=True, nullable=False)

    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    access_token_expire_at = Column(Integer, nullable=False)
    refresh_token_expire_at = Column(Integer, nullable=False)

    logged_at = Column(DateTime(timezone=True), server_default=func.now())

    device = relationship("Device", foreign_keys=[device_id])

    def __repr__(self) -> str:
        return f"<LoginHistory {self.device_i}{self.logged_at }>"

    def to_dict(self) -> str:
        obj = super().to_dict()
        if self.device is not None:
            obj.update({"device": self.device.to_dict()})

        return obj
