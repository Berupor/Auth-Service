import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from src.models.base import AbstractModel


class OAuthRequest(AbstractModel):
    """БД модель запроса кодов по поротоколу OAuth"""

    __tablename__ = "oauth_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider = Column(String, nullable=False)
    fingerprint = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f"<OAuthRequest {self.id}-{self.provider}-{self.fingerprint }>"
