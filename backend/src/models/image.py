from sqlmodel import Field, SQLModel, Column, Integer, ForeignKey

from src.models.base import Base


class ImageBase(SQLModel):
    name: str


class Image(ImageBase, Base, table=True):
    size: str
    file_id: int = Field(default=None, sa_column=Column(
        Integer, ForeignKey("file.id", ondelete="CASCADE"), nullable=False))
