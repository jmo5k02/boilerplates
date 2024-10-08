"""init

Revision ID: 8c24e41afaa9
Revises: 
Create Date: 2024-08-25 22:07:14.053126

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.src.api_core.db.database import Base

# revision identifiers, used by Alembic.
revision: str = "8c24e41afaa9"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "summary",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("summary", sa.String(), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=False),
        sa.Column("address", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user")
    op.drop_table("summary")
    # ### end Alembic commands ###
