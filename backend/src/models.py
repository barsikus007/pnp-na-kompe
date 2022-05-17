from datetime import datetime
from sqlmodel import SQLModel, Field
from pydantic import EmailStr


__all__ = ['User', 'File']


class Base(SQLModel):
    id: int | None = Field(default=None, primary_key=True, nullable=False)
    date_create: datetime | None
    date_update: datetime | None


class ReadBase(SQLModel):
    id: int = Field(default=None, primary_key=True, nullable=False)
    date_create: datetime
    date_update: datetime


class UserBase(SQLModel):
    name: str
    email: EmailStr
    phone: str
    password: str


class User(UserBase, Base, table=True):
    pass


class UserCreate(UserBase):
    pass


class UserRead(ReadBase, UserBase):
    pass


class FileBase(SQLModel):
    name: str
    path: str


class File(FileBase, Base, table=True):
    pass


class FileCreate(FileBase):
    pass


class FileRead(ReadBase, FileBase):
    pass


class ImageBase(SQLModel):
    name: str
    size: str
    file_id: int = Field(default=None, foreign_key='file.id', nullable=False)
    parent: int
    child: int


class Image(ImageBase, Base, table=True):
    pass


class ImageCreate(ImageBase):
    pass


class ImageRead(ReadBase, ImageBase):
    pass


class UserFavoriteBase(SQLModel):
    user_id: int = Field(default=None, foreign_key='user.id', nullable=False)
    image_id: int = Field(default=None, foreign_key='image.id', nullable=False)


class UserFavorite(UserFavoriteBase, Base, table=True):
    pass


class UserFavoriteCreate(UserFavoriteBase):
    pass


class UserFavoriteRead(ReadBase, UserFavoriteBase):
    pass


class ClientBase(SQLModel):
    client_id: str
    secret: str


class Client(ClientBase, Base, table=True):
    pass


class ClientCreate(ClientBase):
    pass


class ClientRead(ReadBase, ClientBase):
    pass


class AccessTokenBase(SQLModel):
    token: str
    client: int = Field(default=None, foreign_key='client.id', nullable=False)
    expires_at: datetime
    user_id: int = Field(default=None, foreign_key='user.id', nullable=False)


class AccessToken(AccessTokenBase, Base, table=True):
    pass


class AccessTokenCreate(AccessTokenBase):
    pass


class AccessTokenRead(ReadBase, AccessTokenBase):
    pass


class RefreshTokenBase(SQLModel):
    token: str
    client: int = Field(default=None, foreign_key='client.id', nullable=False)
    expires_at: datetime
    user_id: int = Field(default=None, foreign_key='user.id', nullable=False)


class RefreshToken(RefreshTokenBase, Base, table=True):
    pass


class RefreshTokenCreate(RefreshTokenBase):
    pass


class RefreshTokenRead(ReadBase, RefreshTokenBase):
    pass


if __name__ == '__main__':
    print(UserFavoriteRead)
