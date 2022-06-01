from sqlmodel import Field, SQLModel, Column, Integer, ForeignKey

from src.models.base import Base


class UserFavoriteBase(SQLModel):
    user_id: int
    image_id: int


class UserFavorite(UserFavoriteBase, Base, table=True):
    user_id: int = Field(default=None, sa_column=Column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False))
    image_id: int = Field(default=None, sa_column=Column(
        Integer, ForeignKey("image.id", ondelete="CASCADE"), nullable=False))
