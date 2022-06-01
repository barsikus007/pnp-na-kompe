import asyncio
from pathlib import Path

from PIL import UnidentifiedImageError
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, Params
from sqlmodel.ext.asyncio.session import AsyncSession

from src import crud
from src.api import deps
from src.models.user import User
from src.models.image import Image
from src.schemas.image import IImageCreate, IImageRead, IImageUpdate, IImageReadFav
from src.schemas.common import (
    IGetResponseBase,
    IPostResponseBase,
    IPutResponseBase,
    IDeleteResponseBase,
    SortBy,
    SortDirection,
)
from src.utils import resize_image


router = APIRouter()


@router.get("/", response_model=IGetResponseBase[Page[IImageReadFav]])
async def read_images_list(
    *,
    sort_by: SortBy = SortBy.id,
    sort_direction: SortDirection = SortDirection.asc,
    params: Params = Depends(),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    images = await crud.image.get_multi_featured(
        db, params=params, current_user=current_user,
        sort_by=sort_by, sort_direction=sort_direction)
    return IGetResponseBase[Page[IImageReadFav]](data=images)


@router.post("/", response_model=IPostResponseBase[IImageRead])
async def create_image(
    *,
    image: IImageCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    file = await crud.file.get(db, id_=image.file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    try:
        loop = asyncio.get_running_loop()
        width, height, sizes = await loop.run_in_executor(None, resize_image, Path(file.path))
    except UnidentifiedImageError as e:
        raise HTTPException(status_code=406, detail="This file is not image") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e)} - {e} from image convertor") from e

    new_image = Image(
        name=image.name,
        file_id=image.file_id,
        size=f"{width}x{height}",
    )
    image_db = await crud.image.create(db, obj_in=new_image)
    image_ret = IImageRead(
        id=image_db.id,
        name=image_db.name,
        size=image_db.size,
        sizes=sizes,
        file_id=image_db.file_id,
    )
    return IPostResponseBase[IImageRead](data=(image_ret))


@router.delete("/{image_id}", response_model=IDeleteResponseBase[IImageRead])
async def remove_image(
    *,
    image_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    image = await crud.image.get(db, id_=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    file = await crud.file.get(db, id_=image.file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    if not current_user.is_superuser and current_user.id != file.owner_id:
        raise HTTPException(status_code=403, detail="You cannot remove this image")
    image = await crud.image.remove(db, id_=image_id)
    return IDeleteResponseBase[IImageRead](
        data=image
    )


@router.get("/{image_id}", response_model=IGetResponseBase[IImageRead])
async def get_image_by_id(
    *,
    image_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    image = await crud.image.get(db, id_=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return IGetResponseBase[IImageRead](data=image)


@router.put("/{image_id}", response_model=IPutResponseBase[IImageRead])
async def update_image(
    *,
    db: AsyncSession = Depends(deps.get_db),
    image_id: int,
    image_in: IImageUpdate,
    current_user: User = Depends(deps.get_current_active_user),
):
    image = await crud.image.get(db, id_=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image no found")
    file = await crud.file.get(db, id_=image.file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    if not current_user.is_superuser and current_user.id != file.owner_id:
        raise HTTPException(status_code=403, detail="You cannot update this image")
    image = await crud.image.update(db, obj_db=image, obj_in=image_in)
    return IPutResponseBase[IImageRead](data=image)
