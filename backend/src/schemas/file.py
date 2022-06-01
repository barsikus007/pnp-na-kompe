from pydantic import BaseModel

from src.models.file import FileBase


class IFileCreate(FileBase):
    owner_id: int


class IFileRead(FileBase):
    id: int


class IFileUpdate(BaseModel):
    name: str
