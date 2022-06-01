from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.init_db import init_db
from src.main import app
from src.api.deps import get_db
from src.core.config import settings


sync_engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})

engine = create_async_engine("sqlite+aiosqlite:///./test.db", echo=settings.DEBUG)

# https://github.com/tiangolo/sqlmodel/issues/54
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, autoflush=False, expire_on_commit=False)  # type: ignore

SQLModel.metadata.create_all(sync_engine)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.mark.asyncio
async def test_get_token():
    async with TestingSessionLocal() as session:
        await init_db(session)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            f"{settings.API_V1_STR}/login",
            json={"email": settings.FIRST_SUPERUSER_EMAIL, "password": settings.FIRST_SUPERUSER_PASSWORD},
        )
        assert response.status_code == 201, response.text
        ac.headers["Authorization"] = f'Bearer {response.json()["data"]["access_token"]}'
        response = await ac.get(
            f"{settings.API_V1_STR}/users/me",
        )
        assert response.status_code == 200, response.text
        assert response.json()["data"]["email"] == settings.FIRST_SUPERUSER_EMAIL, response.text
        user_id = 2
        test_user = {
            "email": "user@example.com",
            "name": "string",
            "phone": "string",
            "is_superuser": False,
        }
        response = await ac.post(
            f"{settings.API_V1_STR}/users/",
            json=test_user | {"password": "string"}
        )
        assert response.status_code == 200, response.text
        assert response.json()["data"] == test_user | {"id": user_id}, response.text
        response = await ac.get(
            f"{settings.API_V1_STR}/users/{user_id}"
        )
        assert response.status_code == 200, response.text
        assert response.json()["data"] == test_user | {"id": user_id}, response.text
        updated_test_user = {
            "email": "users@example.com",
            "name": "strings",
            "phone": "strings",
            "is_superuser": False,
        }
        response = await ac.put(
            f"{settings.API_V1_STR}/users/{user_id}",
            json=updated_test_user | {"password": "strings"}
        )
        assert response.status_code == 200, response.text
        assert response.json()["data"] == updated_test_user | {"id": user_id}, response.text
        response = await ac.delete(
            f"{settings.API_V1_STR}/users/{user_id}",
        )
        assert response.status_code == 200, response.text
        assert response.json()["data"] == updated_test_user | {"id": user_id}, response.text
