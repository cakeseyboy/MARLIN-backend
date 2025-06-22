#!/usr/bin/env python3
"""
Initialize database tables using SQLAlchemy metadata.
This replaces Alembic for clean database initialization.
"""

import asyncio
import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.models import Base
from app.core.settings import get_settings


async def create_tables() -> None:
    """Create all tables defined in the models."""
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    
    async with engine.begin() as conn:
        print("🗄️  Creating database tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("✅ All tables created successfully!")
        
        # Mark current state as migration head for Alembic
        print("📝 Marking database state for Alembic...")
        await conn.execute(text("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL, CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num))"))
        await conn.execute(text("DELETE FROM alembic_version"))
        await conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('20250622_add_wethr_highs')"))
        print("✅ Database state marked successfully!")


if __name__ == "__main__":
    asyncio.run(create_tables()) 