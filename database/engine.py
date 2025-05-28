import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.models import Base
from database.orm_query import orm_add_banner_description, orm_insert_categories

from common.view import categories, page_description

# Creating database engine
engine = create_async_engine(os.getenv('DB_URL'), echo=True)

# Bind - expecting our engine, class - AsyncSession, expire_in_commit - using session repetitively unless it closes
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def create_db():
    async with engine.begin() as conn:
        # Create all tables, stated in file 'database.py'
        await conn.run_sync(Base.metadata.create_all)

    async with session_maker() as session:
        await orm_insert_categories(session, categories)
        await orm_add_banner_description(session, page_description)


async def drop_db():
    async with engine.begin() as conn:
        # Drop all tables, stated in file 'database.py'
        await conn.run_sync(Base.metadata.drop_all)