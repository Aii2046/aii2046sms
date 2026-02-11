from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.core.config import settings
import json

def json_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""
    return json.dumps(obj, ensure_ascii=False)

engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI, 
    echo=True, 
    poolclass=NullPool,
    json_serializer=json_serializer
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
