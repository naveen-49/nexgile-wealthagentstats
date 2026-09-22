"""seed default application roles

Revision ID: 5b7c9d1e2f30
Revises: 450124338008
Create Date: 2026-09-22

"""
from datetime import datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5b7c9d1e2f30"
down_revision = "450124338008"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    existing_roles = {
        row[0]
        for row in bind.execute(
            sa.text("SELECT name FROM roles")
        ).fetchall()
    }
    default_roles = [
        ("ADMIN", "System administrator"),
        ("ADVISOR", "Financial advisor"),
        ("CLIENT", "Client portal user"),
    ]

    for name, description in default_roles:
        if name not in existing_roles:
            bind.execute(
                sa.text(
                    """
                    INSERT INTO roles (name, description, created_at)
                    VALUES (:name, :description, :created_at)
                    """
                ),
                {
                    "name": name,
                    "description": description,
                    "created_at": datetime.utcnow(),
                },
            )


def downgrade():
    bind = op.get_bind()

    bind.execute(
        sa.text(
            "DELETE FROM roles WHERE name IN "
            "('ADMIN', 'ADVISOR', 'CLIENT')"
        )
    )
