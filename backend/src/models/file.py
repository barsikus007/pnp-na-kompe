from sqlmodel import SQLModel, Field

from src.models.base import Base


class FileBase(SQLModel):
    name: str
    path: str


class File(FileBase, Base, table=True):
    owner_id: int = Field(default=None, foreign_key='user.id', nullable=False)
