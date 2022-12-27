from sqlalchemy import (Boolean, Column, ForeignKey, Integer, String,
                        UniqueConstraint)

from src.models.base import AbstractModel


class Device(AbstractModel):
    """БД модель устройства"""

    __tablename__ = "devices"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "fingerprint",
            name="userdevice_fingeprint_unique_together",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    fingerprint = Column(String, nullable=False)
    is_allowed = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Device {self.fingerprint}>"
