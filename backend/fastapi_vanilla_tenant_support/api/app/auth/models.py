import uuid
from datetime import timedelta, datetime
from typing import Optional
from sqlalchemy import (
    String,
    LargeBinary,
    DateTime,
    UUID,
    UniqueConstraint,
    ForeignKey,
    Boolean,
    Enum as SQLAlchemyEnum,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy_utils import TSVectorType

from app.db.base import Base
from app.db.mixin import TimeStampMixin, UUIDMixin, CrudMixin
from app.tenants.models import Tenant
from app.common.utils.enums import UserRoles
from app.auth.utils import create_access_token, verify_password
from app.settings import settings


class AppUser(Base, TimeStampMixin, UUIDMixin, CrudMixin):
    __table_args__ = {"schema": "core"}

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    salt: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    # System-level superuser flag
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Account status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    failed_login_attempts: Mapped[int] = mapped_column(default=0, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    tenant_associations: Mapped[list["AppUserTenant"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    tenants: Mapped[list[Tenant]] = relationship(
        secondary="core.app_user_tenant",
        back_populates="users",
        viewonly=True,
        lazy="selectin"
    )

    search_vector: Mapped[TSVectorType] = mapped_column(
        TSVectorType("email", weights={"email": "A"}), nullable=True
    )

    def get_tenant_role(self, tenant_slug: str):
        """Get user role for a given tenant"""
        for t in self.tenant_associations:
            if t.tenant.slug == tenant_slug:
                return t.role

    def is_superuser(self):
        return

    def check_password(self, password: str) -> bool:
        if not self.is_active:
            return False

        if self.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            return False

        is_valid = verify_password(bytes(password, "utf-8"), self.password, self.salt)
        if not is_valid:
            self.failed_login_attempts += 1
        else:
            self.failed_login_attempts = 0
            self.last_login = datetime.utcnow()

        return is_valid

    @property
    def token(self) -> str:
        return create_access_token(
            self.email, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )


class AppUserTenant(Base, TimeStampMixin, UUIDMixin):
    __table_args__ = (
        UniqueConstraint(
            "user_id", "tenant_id", name="uq_user_tenant_user_id_tenant_id"
        ),
        {"schema": "core"},
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.app_user.id", ondelete="CASCADE"), primary_key=True
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.tenant.id", ondelete="CASCADE"),primary_key=True
    )

    user: Mapped[AppUser] = relationship(back_populates="tenant_associations")
    tenant: Mapped[Tenant] = relationship(back_populates="user_associations")

    role: Mapped[UserRoles] = mapped_column(
        SQLAlchemyEnum(UserRoles, create_constraint=True, schema="core"),
        default=UserRoles.member,
        nullable=False,
    )
