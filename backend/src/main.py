from uuid import uuid4
from random import choice, randint

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import ORJSONResponse
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from db import get_session
from models import City, User, UserRead


app = FastAPI(
    title='NPN',
    description='pnp na kompe',
    version='8.1',
    openapi_url='/docs/openapi.json',
    default_response_class=ORJSONResponse,
    docs_url='/docs',
    redoc_url=None,
)


@app.get('/api/v1/kek', response_model=dict[str, list])
async def kek_lol(session: AsyncSession = Depends(get_session)):
    cities = [City(name=uuid4().hex[:8]) for _ in range(5)]
    [session.add(city) for city in cities]
    await session.commit()
    users = [User(
        name=uuid4().hex[:8],
        email=f'{uuid4().hex[:8]}@aboba.net',
        phone=randint(8_900_000_00_00, 8_999_999_99_99),
        city_id=choice(cities).id,
    ) for _ in range(10)]
    [session.add(user) for user in users]
    await session.commit()
    return {'lol': cities, 'kek': users}


@app.get('/api/v1/get_users_by_city_id/{city_id}', response_model=list[UserRead])
async def get_user_by_city_id(city_id: int, session: AsyncSession = Depends(get_session)):
    user = (await session.exec(select(User).where(User.city_id == city_id))).all()
    if not user:
        raise HTTPException(status_code=404, detail="ПользователИ с таким городом не найденЫ")
    return user


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', reload=True)  # , log_level='critical')
