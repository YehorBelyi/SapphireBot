import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.models import Base

# Creating database engine
engine = create_async_engine(os.getenv('DB_URL'), echo=True)

# Bind - expecting our engine, class - AsyncSession, expire_in_commit - using session repetitively unless it closes
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def create_db():
    async with engine.begin() as conn:
        # Create all tables, stated in file 'database.py'
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    async with engine.begin() as conn:
        # Drop all tables, stated in file 'database.py'
        await conn.run_sync(Base.metadata.drop_all)