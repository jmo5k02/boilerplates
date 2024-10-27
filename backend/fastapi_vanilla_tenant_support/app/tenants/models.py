from slugify import slugify

from sqlalchemy import String, Boolean
from sqlalchemy.event import listen
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import TSVectorType

from app.db.base import Base
from app.db.mixin import TimeStampMixin, CrudMixin, UUIDMixin


class Tenant(CrudMixin, TimeStampMixin, UUIDMixin, Base):
    """Tenant model"""
    name: Mapped[str] = mapped_column(String, unique=True)
    slug: Mapped[str] = mapped_column(String, unique=True)
    default: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str] = mapped_column(String, nullable=True)

    search_vector: Mapped = mapped_column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )

def generate_slug(target, value, oldvalue, initiator):
    """Creates a reasonable slug based on organization name."""
    if value and (not target.slug or value != oldvalue):
        target.slug = slugify(value, separator="_")


listen(Tenant.name, "set", generate_slug)