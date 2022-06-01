from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, Params
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src import crud
from src.api import deps
from src.models.user import User
from src.models.user_favorite import UserFavorite
from src.schemas.user_favorite import IUserFavoriteCreate, IUserFavoriteRead
from src.schemas.common import (
    IGetResponseBase,
    IPostResponseBase,
    IDeleteResponseBase,
    SortBy,
    SortDirection,
)


router = APIRouter()


@router.get("/", response_model=IGetResponseBase[Page[IUserFavoriteRead]])
async def read_user_favorites_list(
    *,
    sort_by: SortBy = SortBy.id,
    sort_direction: SortDirection = SortDirection.asc,
    params: Params = Depends(),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    user_favorites = await crud.user_favorite.get_multi(
        db, params=params,
        query=select(UserFavorite).order_by(getattr(getattr(UserFavorite, sort_by), sort_direction)()))
    return IGetResponseBase[Page[IUserFavoriteRead]](data=user_favorites)


@router.post("/", response_model=IPostResponseBase[IUserFavoriteRead])
async def create_user_favorite(
    *,
    user_favorite: IUserFavoriteCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    user = await crud.user.get(db, id_=user_favorite.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    image = await crud.image.get(db, id_=user_favorite.image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    user_favorite_db = await crud.user_favorite.create(db, obj_in=user_favorite)
    return IPostResponseBase[IUserFavoriteRead](data=user_favorite_db)


@router.delete("/{user_favorite_id}", response_model=IDeleteResponseBase[IUserFavoriteRead])
async def remove_user_favorite(
    *,
    user_favorite_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    user_favorite = await crud.user_favorite.get(db, id_=user_favorite_id)
    if not user_favorite:
        raise HTTPException(status_code=404, detail="UserFavorite not found")
    if not current_user.is_superuser and current_user.id != user_favorite.user_id:
        raise HTTPException(status_code=403, detail="You cannot remove this user_favorite")
    user_favorite = await crud.user_favorite.remove(db, id_=user_favorite_id)
    return IDeleteResponseBase[IUserFavoriteRead](
        data=user_favorite
    )


@router.get("/{user_favorite_id}", response_model=IGetResponseBase[IUserFavoriteRead])
async def get_user_favorite_by_id(
    *,
    user_favorite_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    user_favorite = await crud.user_favorite.get(db, id_=user_favorite_id)
    return IGetResponseBase[IUserFavoriteRead](data=user_favorite)
