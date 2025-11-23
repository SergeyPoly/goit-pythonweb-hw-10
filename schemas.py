from pydantic import BaseModel, Field, EmailStr
from datetime import date, datetime
from typing import Optional


class UserSchema(BaseModel):
    username: str = Field(min_length=5, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6)


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ContactBase(BaseModel):
    first_name: str = Field(min_length=3, max_length=50)
    last_name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    phone_number: str = Field(min_length=10, max_length=15)
    birthday: date
    additional_data: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(ContactBase):
    pass


class ContactResponse(ContactBase):
    id: int

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    avatar: Optional[str] = None
    confirmed: bool

    class Config:
        from_attributes = True
