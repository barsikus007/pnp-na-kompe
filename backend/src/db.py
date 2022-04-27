from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import Select, SelectOfScalar

from settings import settings


Select.inherit_cache = True
SelectOfScalar.inherit_cache = True

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)


async def get_session() -> AsyncSession:
    try:
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        print('Соединение с БД установлено', flush=True)
        async with async_session() as session:
            yield session
    except:
        print('Что-то пошло не так', flush=True)
