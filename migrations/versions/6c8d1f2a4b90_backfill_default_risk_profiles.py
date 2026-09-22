"""backfill default risk profiles for existing clients

Revision ID: 6c8d1f2a4b90
Revises: 5b7c9d1e2f30
Create Date: 2026-09-22

"""
from alembic import op
import sqlalchemy as sa


revision = "6c8d1f2a4b90"
down_revision = "5b7c9d1e2f30"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    bind.execute(
        sa.text(
            """
            INSERT INTO risk_profiles (client_id, score, category, created_at)
            SELECT c.id, 50, 'MODERATE', UTC_TIMESTAMP()
            FROM clients c
            LEFT JOIN risk_profiles rp ON rp.client_id = c.id
            WHERE rp.id IS NULL
            """
        )
    )


def downgrade():
    # Do not remove existing client risk profiles on downgrade.
    pass
