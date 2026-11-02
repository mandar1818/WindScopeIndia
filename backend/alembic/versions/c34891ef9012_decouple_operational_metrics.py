"""decouple operational metrics and separate demand from generation

Revision ID: c34891ef9012
Revises: b12984cf5102
Create Date: 2026-11-01 14:55:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision: str = 'c34891ef9012'
down_revision: Union[str, None] = 'b12984cf5102'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create table daily_operational_metrics
    op.create_table(
        'daily_operational_metrics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('geography_id', sa.Integer(), nullable=False),
        sa.Column('delivery_date', sa.Date(), nullable=False),
        sa.Column('energy_met_mu', sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column('peak_demand_met_mw', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('peak_shortage_mw', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('energy_shortage_mu', sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column('source_file_id', sa.Integer(), nullable=True),
        sa.Column('source_provenance', sa.String(length=100), server_default='Grid Controller of India Limited (NLDC Daily PSP)', nullable=False),
        sa.Column('data_classification', sa.String(length=50), server_default='VERIFIED_OFFICIAL', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['geography_id'], ['geographies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_file_id'], ['source_files.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('geography_id', 'delivery_date', name='uq_daily_operational_metrics')
    )
    op.create_index('idx_daily_operational_geo_date', 'daily_operational_metrics', ['geography_id', 'delivery_date'], unique=False)

    # 2. Add data_classification and source_file_id to generation_daily
    with op.batch_alter_table('generation_daily', schema=None) as batch_op:
        batch_op.add_column(sa.Column('data_classification', sa.String(length=50), server_default='VERIFIED_OFFICIAL', nullable=False))
        batch_op.add_column(sa.Column('source_file_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_gen_daily_source_file', 'source_files', ['source_file_id'], ['id'], ondelete='SET NULL')

    # 3. Data Migration: Copy DEMAND_MET rows from generation_daily into daily_operational_metrics
    conn = op.get_bind()
    conn.execute(sa.text("""
        INSERT INTO daily_operational_metrics (geography_id, delivery_date, energy_met_mu, source_provenance, data_classification)
        SELECT geography_id, delivery_date, generation_mu, source_provenance, 'VERIFIED_OFFICIAL'
        FROM generation_daily
        WHERE source_code = 'DEMAND_MET'
    """))

    # Delete DEMAND_MET rows from generation_daily
    conn.execute(sa.text("DELETE FROM generation_daily WHERE source_code = 'DEMAND_MET'"))

    # Delete DEMAND_MET from energy_sources
    conn.execute(sa.text("DELETE FROM energy_sources WHERE source_code = 'DEMAND_MET'"))


def downgrade() -> None:
    conn = op.get_bind()

    # 1. Restore DEMAND_MET in energy_sources
    conn.execute(sa.text("""
        INSERT OR IGNORE INTO energy_sources (source_code, display_name, unit, is_variable_re)
        VALUES ('DEMAND_MET', 'Total System Demand Met', 'MU', 0)
    """))

    # 2. Restore DEMAND_MET rows in generation_daily
    conn.execute(sa.text("""
        INSERT INTO generation_daily (geography_id, source_code, delivery_date, generation_mu, source_provenance, data_classification)
        SELECT geography_id, 'DEMAND_MET', delivery_date, energy_met_mu, source_provenance, data_classification
        FROM daily_operational_metrics
    """))

    # 3. Remove columns from generation_daily
    with op.batch_alter_table('generation_daily', schema=None) as batch_op:
        batch_op.drop_constraint('fk_gen_daily_source_file', type_='foreignkey')
        batch_op.drop_column('source_file_id')
        batch_op.drop_column('data_classification')

    # 4. Drop daily_operational_metrics
    op.drop_index('idx_daily_operational_geo_date', table_name='daily_operational_metrics')
    op.drop_table('daily_operational_metrics')

