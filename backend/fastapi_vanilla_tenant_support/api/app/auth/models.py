from datetime import timedelta
from sqlalchemy import (
    String,
    LargeBinary,
    UUID,
    UniqueConstraint,
    ForeignKey,
    Enum as SQLAlchemyEnum,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy_utils import TSVectorType

from app.db.base import Base
from app.db.mixin import TimeStampMixin, UUIDMixin, CrudMixin
from app.tenants.models import Tenant
from app.utils.enums import UserRoles
from app.auth.utils import create_access_token, verify_password
from app.settings import settings


class AppUser(Base, TimeStampMixin, UUIDMixin, CrudMixin):
    __table_args__ = {"schema": "core"}

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    salt: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    tenants: Mapped[list["AppUserTenant"]] = relationship(
        "AppUserTenant", back_populates="user", lazy="selectin"
    )

    search_vector: Mapped[TSVectorType] = mapped_column(
        TSVectorType("email", weights={"email": "A"}), nullable=True
    )

    def get_tenant_role(self, tenant_slug: str):
        """Get user role for a given tenant"""
        for t in self.tenants:
            if t.tenant.slug == tenant_slug:
                return t.role
    
    def check_password(self, password: str):
        return verify_password(bytes(password, 'utf-8'), self.password, self.salt)

    @property
    def token(self):
        return create_access_token(self.email, timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES))


class AppUserTenant(Base, TimeStampMixin, UUIDMixin):
    __table_args__ = (
        UniqueConstraint(
            "user_id", "tenant_id", name="uq_user_tenant_user_id_tenant_id"
        ),
        {"schema": "core"},
    )

    user_id: Mapped[str] = mapped_column(UUID, ForeignKey(AppUser.id))
    user = relationship(AppUser, back_populates="tenants", lazy="selectin")

    tenant_id: Mapped[str] = mapped_column(UUID, ForeignKey(Tenant.id))
    tenant: Mapped[Tenant] = relationship(
        Tenant, back_populates="users", lazy="selectin"
    )

    role: Mapped[UserRoles] = mapped_column(
        SQLAlchemyEnum(UserRoles, create_constraint=True, schema="core"),
        default=UserRoles.member,
        nullable=False,
    )

