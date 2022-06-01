from src.crud.base import CRUDBase
from src.models.file import File
from src.schemas.file import IFileCreate, IFileUpdate


class CRUDFile(CRUDBase[File, IFileCreate, IFileUpdate]):
    pass


file = CRUDFile(File)
