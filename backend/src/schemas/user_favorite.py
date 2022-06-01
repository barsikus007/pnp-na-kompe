from pydantic import BaseModel

from src.models.user_favorite import UserFavoriteBase


class IUserFavoriteCreate(UserFavoriteBase):
    pass


class IUserFavoriteRead(UserFavoriteBase):
    id: int


class IUserFavoriteUpdate(BaseModel):
    pass
