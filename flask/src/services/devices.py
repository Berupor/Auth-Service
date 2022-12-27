from src.db.uow import AbstractUnitOfWork
from src.models.device import Device
from src.services.base import BaseService


class DeviceService(BaseService):
    """Сервис для работы с устройствами"""

    _model = Device
    _model_name = "device"

    def get_device_type(self, fingerprint: str) -> str:
        for type in ["smart", "mobile"]:
            if type in fingerprint:
                return type

        return "web"

    def get_or_create_allowed_device(
        self, user_id: int, fingerprint: str
    ) -> tuple[dict, bool]:

        return self.get_or_create(
            query={
                "user_id": user_id,
                "fingerprint": fingerprint,
                "is_allowed": True,
            }
        )


def get_device_service(uow: AbstractUnitOfWork) -> DeviceService:
    return DeviceService(uow)
