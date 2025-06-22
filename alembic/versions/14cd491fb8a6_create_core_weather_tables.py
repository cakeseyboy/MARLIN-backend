"""create core weather tables

Revision ID: 14cd491fb8a6
Revises: 
Create Date: 2025-06-21 20:59:44.559095

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '14cd491fb8a6'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create weather_stations table
    op.create_table(
        'weather_stations',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('code', sa.String(5), unique=True, index=True, nullable=False),
        sa.Column('name', sa.String(64), nullable=False),
        sa.Column('lat', sa.Float(), nullable=False),
        sa.Column('lon', sa.Float(), nullable=False),
        sa.Column('timezone', sa.String(32), nullable=False),
        sa.Column('coastal_distance_km', sa.Float(), nullable=False),
    )
    
    # Create tmax_calculations table
    op.create_table(
        'tmax_calculations',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('station_id', sa.Integer(), nullable=False),
        sa.Column('cli_forecast', sa.Float(), nullable=False),
        sa.Column('observed_high', sa.Float(), nullable=True),
        sa.Column('method', sa.String(32), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('raw_payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    )
    
    # Create weather_forecasts table
    op.create_table(
        'weather_forecasts',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('station_id', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(16), nullable=False),
        sa.Column('run_timestamp', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('data', sa.JSON(), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('weather_forecasts')
    op.drop_table('tmax_calculations')
    op.drop_table('weather_stations')
