"""add weather fields

Revision ID: b12984cf5102
Revises: af8f7710238a
Create Date: 2026-11-01 13:54:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b12984cf5102'
down_revision: Union[str, None] = 'af8f7710238a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new weather observation columns
    with op.batch_alter_table("weather_observations", schema=None) as batch_op:
        batch_op.add_column(sa.Column("wind_speed_10m_ms", sa.Numeric(precision=6, scale=2), nullable=True))
        batch_op.add_column(sa.Column("wind_direction_deg", sa.Numeric(precision=5, scale=1), nullable=True))
        batch_op.add_column(sa.Column("precipitation_mm", sa.Numeric(precision=6, scale=2), nullable=True))
        batch_op.add_column(sa.Column("latitude", sa.Numeric(precision=8, scale=4), nullable=True))
        batch_op.add_column(sa.Column("longitude", sa.Numeric(precision=8, scale=4), nullable=True))
        batch_op.add_column(sa.Column("weather_model", sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column("record_type", sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column("retrieval_timestamp", sa.DateTime(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("weather_observations", schema=None) as batch_op:
        batch_op.drop_column("retrieval_timestamp")
        batch_op.drop_column("record_type")
        batch_op.drop_column("weather_model")
        batch_op.drop_column("longitude")
        batch_op.drop_column("latitude")
        batch_op.drop_column("precipitation_mm")
        batch_op.drop_column("wind_direction_deg")
        batch_op.drop_column("wind_speed_10m_ms")

