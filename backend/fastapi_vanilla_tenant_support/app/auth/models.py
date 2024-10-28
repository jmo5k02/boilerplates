from sqlalchemy import String, LargeBinary, UUID, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy_utils import TSVectorType

from app.db.base import Base
from app.db.mixin import TimeStampMixin, UUIDMixin
from app.core.enums import UserRoles


class User(TimeStampMixin, UUIDMixin, Base):
    __table_args__ = {"schema": "core"}

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(LargeBinary, nullable=False)

    search_vector = mapped_column(
        TSVectorType("email", weights={"email": "A"})
    )


class UserTenant(TimeStampMixin, UUIDMixin, Base):
    __table_args__ = {"schema": "core"}

    user_id: Mapped[str] = mapped_column(UUID, nullable=False)
    user = relationship("User", back_populates="tenants")

    tenant_id: Mapped[str] = mapped_column(UUID, nullable=False)
    tenant = relationship("Tenant", back_populates="users")

    role: Mapped[str] = mapped_column(String(255), default=UserRoles.member)

    __table_args__ = (
        UniqueConstraint("user_id", "tenant_id", name="uq_user_tenant_user_id_tenant_id"),
    )