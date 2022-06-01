import os
import shutil
from uuid import uuid4
from typing import IO
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi_pagination import Page, Params
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src import crud
from src.api import deps
from src.utils import files_folder
from src.models.user import User
from src.models.file import File
from src.schemas.file import IFileCreate, IFileRead, IFileUpdate
from src.schemas.common import (
    IGetResponseBase,
    IPostResponseBase,
    IPutResponseBase,
    IDeleteResponseBase,
    SortBy,
    SortDirection,
)


router = APIRouter()


@router.get("/", response_model=IGetResponseBase[Page[IFileRead]])
async def read_files_list(
    *,
    sort_by: SortBy = SortBy.id,
    sort_direction: SortDirection = SortDirection.asc,
    params: Params = Depends(),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    files = await crud.file.get_multi(
        db, params=params,
        query=select(File).order_by(getattr(getattr(File, sort_by), sort_direction)()))
    return IGetResponseBase[Page[IFileRead]](data=files)


@router.post("/", response_model=IPostResponseBase[IFileRead])
async def create_file(
    *,
    file: UploadFile,
    file_size: int = Depends(deps.valid_content_length),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    real_file_size = 0
    temp: IO = NamedTemporaryFile(delete=False)
    for chunk in file.file:
        real_file_size += len(chunk)
        if real_file_size > file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Too large"
            )
        temp.write(chunk)
    filename = files_folder / f"{uuid4()}.{file.filename.split('.')[-1]}"
    shutil.move(temp.name, filename)
    os.chmod(filename, 0o644)

    new_file = IFileCreate(
        name=file.filename,
        path=str(filename),
        owner_id=current_user.id,
    )
    file_db = await crud.file.create(db, obj_in=new_file)
    return IPostResponseBase[IFileRead](data=file_db)


@router.delete("/{file_id}", response_model=IDeleteResponseBase[IFileRead])
async def remove_file(
    *,
    file_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    file = await crud.file.get(db, id_=file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    if not current_user.is_superuser and current_user.id != file.id:
        raise HTTPException(status_code=403, detail="You cannot remove this file")
    filename = Path(file.path)
    filename.unlink()
    for filename_child in filename.parent.glob(filename.with_suffix("").name + "*"):
        filename_child.unlink()
    file = await crud.file.remove(db, id_=file_id)
    return IDeleteResponseBase[IFileRead](
        data=file
    )


@router.get("/{file_id}", response_model=IGetResponseBase[IFileRead])
async def get_file_by_id(
    *,
    file_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    file = await crud.file.get(db, id_=file_id)
    return IGetResponseBase[IFileRead](data=file)


@router.put("/{file_id}", response_model=IPutResponseBase[IFileRead])
async def update_file(
    *,
    db: AsyncSession = Depends(deps.get_db),
    file_id: int,
    file_in: IFileUpdate,
    current_user: User = Depends(deps.get_current_active_user),
):
    file = await crud.file.get(db, id_=file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    if not current_user.is_superuser and current_user.id != file.owner_id:
        raise HTTPException(status_code=403, detail="You cannot update this file")
    file = await crud.file.update(db, obj_db=file, obj_in=file_in)
    return IPutResponseBase[IFileRead](data=file)
