from src.crud.base import CRUDBase
from src.models.user_favorite import UserFavorite
from src.schemas.user_favorite import IUserFavoriteCreate, IUserFavoriteUpdate


class CRUDUserFavorite(CRUDBase[UserFavorite, IUserFavoriteCreate, IUserFavoriteUpdate]):
    pass


user_favorite = CRUDUserFavorite(UserFavorite)
