from sqlmodel import SQLModel, Field
from pydantic import EmailStr, condecimal

__all__ = ['City', 'User']


class CityBase(SQLModel):
    name: str


class City(CityBase, table=True):
    id: int | None = Field(default=None, primary_key=True, nullable=False)


class CityCreate(CityBase):
    pass


class CityRead(CityBase):
    id: int



class UserBase(SQLModel):
    name: str
    email: EmailStr
    phone: condecimal(max_digits=11)
    city_id: int | None = Field(default=None, foreign_key='city.id', nullable=False)



class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True, nullable=False)


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int
