from sqlalchemy import String, LargeBinary, UUID, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy_utils import TSVectorType

from app.db.base import Base
from app.db.mixin import TimeStampMixin, UUIDMixin, CrudMixin
from app.tenants.models import Tenant
from app.utils.enums import UserRoles


class AppUser(Base, TimeStampMixin, UUIDMixin, CrudMixin):
    __table_args__ = {"schema": "core"}

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(LargeBinary, nullable=False)

    tenants: Mapped[list["AppUserTenant"]] = relationship("AppUserTenant", back_populates="user")

    search_vector: Mapped[TSVectorType] = mapped_column(
        TSVectorType("email", weights={"email": "A"})
    )


class AppUserTenant(Base, TimeStampMixin, UUIDMixin):
    __table_args__ = (
        UniqueConstraint("user_id", "tenant_id", name="uq_user_tenant_user_id_tenant_id"),
        {"schema": "core"},
    )

    user_id: Mapped[str] = mapped_column(UUID, ForeignKey(AppUser.id))
    user = relationship(AppUser, back_populates="tenants")

    tenant_id: Mapped[str] = mapped_column(UUID, ForeignKey(Tenant.id))
    tenant: Mapped[Tenant] = relationship(Tenant, back_populates="users")

    role: Mapped[str] = mapped_column(String(255), default=UserRoles.member)
