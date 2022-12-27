from sqlalchemy import Column, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from src.models.base import AbstractModel


class SocialAccount(AbstractModel):
    """БД модель аккаунта в социальной сети"""

    __tablename__ = "social_accounts"
    __table_args__ = (
        UniqueConstraint("social_id", "provider", name="social_pk"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    social_id = Column(Text, nullable=False)
    provider = Column(Text, nullable=False)

    user = relationship(
        "User",
        back_populates="social_accounts",
        lazy="subquery",
    )

    def __repr__(self):
        return f"<SocialAccount {self.provider}:{self.user_id}>"
