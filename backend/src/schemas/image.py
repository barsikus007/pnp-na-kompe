from pydantic import BaseModel

from src.models.image import ImageBase


class ImageSizes(BaseModel):
    size_2560: str | None = None
    size_1920: str | None = None
    size_1280: str | None = None


class IImageCreate(ImageBase):
    file_id: int
    name: str


class IImageRead(ImageBase):
    id: int
    file_id: int
    size: str
    sizes: ImageSizes | None


class IImageReadFav(IImageRead):
    is_favorite: bool


class IImageUpdate(BaseModel):
    name: str
