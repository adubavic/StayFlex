"""Database Initialization Script - Creates all tables using SQLAlchemy ORM"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from database import Base
import models  # Import models to register them with Base

DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres:postgres@localhost:5432/voucher_marketplace'
)

if DATABASE_URL.startswith('postgresql://'):
    ASYNC_DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')
else:
    ASYNC_DATABASE_URL = DATABASE_URL


async def create_tables():
    """Create all tables defined in models.py"""
    engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("All tables created successfully!")


if __name__ == "__main__":
    asyncio.run(create_tables())
