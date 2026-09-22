"""add email verification fields

Revision ID: 450124338008
Revises: cda029f2f998
Create Date: 2026-09-22 14:01:01.455661

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '450124338008'
down_revision = 'cda029f2f998'
branch_labels = None
depends_on = None

def upgrade():
    from sqlalchemy import inspect

    bind = op.get_bind()
    inspector = inspect(bind)

    columns = {
        column["name"]
        for column in inspector.get_columns("users")
    }

    if "email_verified" not in columns:
        op.add_column(
            "users",
            sa.Column(
                "email_verified",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false()
            )
        )

def downgrade():
    from sqlalchemy import inspect

    bind = op.get_bind()
    inspector = inspect(bind)

    columns = {
        column["name"]
        for column in inspector.get_columns("users")
    }

    if "email_verified" in columns:
        op.drop_column("users", "email_verified")