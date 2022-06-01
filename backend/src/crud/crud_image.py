from fastapi_pagination import resolve_params, create_page
from fastapi_pagination.bases import AbstractParams, AbstractPage
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from src.crud.base import CRUDBase
from src.models.user import User
from src.models.file import File
from src.models.image import Image
from src.models.user_favorite import UserFavorite
from src.schemas.common import SortBy, SortDirection
from src.schemas.image import IImageCreate, IImageRead, IImageReadFav, IImageUpdate
from src.utils import generate_sizes


class CRUDImage(CRUDBase[Image, IImageCreate, IImageUpdate]):
    async def get(
            self, db: AsyncSession, *, id_: str | int
    ) -> IImageRead | None:
        resp = (await db.exec(select(Image, File).where(
            Image.id == id_, Image.file_id == File.id
        ))).first()
        if resp is None:
            return
        image_, file = resp
        return IImageRead(
            id=image_.id,
            name=image_.name,
            size=image_.size,
            sizes=generate_sizes(image_, file),
            file_id=file.id,
        )

    async def get_multi_featured(
            self, db: AsyncSession, *,
            sort_by: SortBy, sort_direction: SortDirection, params: AbstractParams, current_user: User
    ) -> AbstractPage[IImageReadFav]:
        query = select(UserFavorite).where(UserFavorite.user_id == current_user.id)
        user_fav_query = [_.image_id for _ in (await db.exec(query)).all()]  # type: ignore
        print(user_fav_query)
        query = select(Image, File).where(
            Image.file_id == File.id
        ).distinct(Image.id).order_by(
            getattr(getattr(Image, sort_by), sort_direction)())

        params = resolve_params(params)
        raw_params = params.to_raw_params()
        total = await db.scalar(select(func.count("*")).select_from(query.subquery()))
        query_response = await db.exec(query.limit(raw_params.limit).offset(raw_params.offset))

        items = [
            IImageReadFav(
                id=image_.id,
                name=image_.name,
                size=image_.size,
                sizes=generate_sizes(image_, file),
                is_favorite=image_.id in user_fav_query,
                file_id=file.id,
            ) for image_, file in query_response.unique().all()]

        return create_page(items, total, params)


image = CRUDImage(Image)
