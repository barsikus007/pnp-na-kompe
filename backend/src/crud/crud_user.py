from typing import Any
from datetime import datetime, timezone, timedelta

from pydantic.networks import EmailStr
from fastapi_pagination import resolve_params, create_page
from fastapi_pagination.bases import AbstractParams, AbstractPage
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from src.crud.base import CRUDBase
from src.models.user import User
from src.models.file import File
from src.models.image import Image
from src.schemas.common import SortBy, SortDirection
from src.schemas.user import IUserCreate, IUserUpdate
from src.core.security import verify_password, get_password_hash


class CRUDUser(CRUDBase[User, IUserCreate, IUserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        users = await db.exec(select(User).where(User.email == email))  # type: ignore
        return users.first()
    
    async def get_multi_recent(
            self, db: AsyncSession, *,
            sort_by: SortBy, sort_direction: SortDirection, params: AbstractParams
        ) -> AbstractPage[User]:
        query = select(User, File, Image).where(
            User.id == File.owner_id, File.id == Image.file_id,
            Image.date_create > datetime.now(timezone.utc) - timedelta(days=7),
        ).distinct(User.id).order_by(
            getattr(getattr(User, sort_by), sort_direction)())

        params = resolve_params(params)
        raw_params = params.to_raw_params()
        total = await db.scalar(select(func.count("*")).select_from(query.subquery()))
        query_response = await db.exec(query.limit(raw_params.limit).offset(raw_params.offset))

        items = [_ for _, *__ in query_response.unique().all()]

        return create_page(items, total, params)

    async def create(self, db: AsyncSession, *, obj_in: IUserCreate) -> User:
        obj_db = User(
            name=obj_in.name,
            email=obj_in.email,
            phone=obj_in.phone,
            hashed_password=get_password_hash(obj_in.password),
            is_superuser=obj_in.is_superuser,
        )
        db.add(obj_db)
        await db.commit()
        await db.refresh(obj_db)
        return obj_db

    async def update(
        self,
        db: AsyncSession,
        *,
        obj_db: User,
        obj_in: IUserUpdate | dict[str, Any]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return await super().update(db, obj_db=obj_db, obj_in=update_data)

    async def authenticate(
        self, db: AsyncSession, *, email: EmailStr, password: str
    ) -> User | None:
        user_auth = await self.get_by_email(db, email=email)
        if not user_auth:
            return None
        if not verify_password(password, user_auth.hashed_password):
            return None
        return user_auth


user = CRUDUser(User)
