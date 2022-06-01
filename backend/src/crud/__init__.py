from .crud_user import user
from .crud_file import file
from .crud_image import image
from .crud_user_favorite import user_favorite


# For a new basic set of CRUD operations you could just do

# from .base import CRUDBase
# from app.models.item import Item
# from app.schemas.item import ItemCreate, ItemUpdate

# item = CRUDBase[Item, ItemCreate, ItemUpdate](Item)
