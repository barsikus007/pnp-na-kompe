import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import ORJSONResponse
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from db import get_session
from models import User, UserRead


app = FastAPI(
    title='PNP',
    description='pnp na kompe',
    version='8.1',
    openapi_url='/docs/openapi.json',
    default_response_class=ORJSONResponse,
    docs_url='/docs',
    redoc_url=None,
)


@app.get('/api/v1/kek', response_model=dict[str, list])
async def kek_lol(session: AsyncSession = Depends(get_session)):
    return {'lol': 'cities', 'kek': 'users'}


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', reload=True)  # , log_level='critical')
