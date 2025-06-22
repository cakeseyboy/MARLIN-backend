"""add wethr_highs table and update tmax_calculations

Revision ID: 20250622_add_wethr_highs
Revises: 14cd491fb8a6
Create Date: 2025-06-22 03:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20250622_add_wethr_highs"
down_revision = "14cd491fb8a6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to tmax_calculations
    op.add_column("tmax_calculations", sa.Column("observed_high", sa.Float(), nullable=True))
    op.add_column("tmax_calculations", sa.Column("size", sa.Float(), nullable=False, server_default="0"))
    
    # Make confidence column non-nullable (it was nullable before)
    op.alter_column("tmax_calculations", "confidence", nullable=False)
    
    # Create wethr_highs table
    op.create_table(
        "wethr_highs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("station_id", sa.Integer(), nullable=False),
        sa.Column("date_iso", sa.String(length=10), nullable=False),
        sa.Column("wethr_high", sa.Float(), nullable=False),
        sa.Column("scraped_at", postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["station_id"], ["weather_stations.id"], ),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_wethr_highs_id"), "wethr_highs", ["id"], unique=False)


def downgrade() -> None:
    # Drop wethr_highs table
    op.drop_index(op.f("ix_wethr_highs_id"), table_name="wethr_highs")
    op.drop_table("wethr_highs")
    
    # Remove columns from tmax_calculations
    op.drop_column("tmax_calculations", "size")
    op.drop_column("tmax_calculations", "observed_high")
    
    # Revert confidence column to nullable
    op.alter_column("tmax_calculations", "confidence", nullable=True) 