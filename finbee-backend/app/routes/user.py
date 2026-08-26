"""
User schema — represents an authenticated FinBee user.
Backed by the `users` collection in MongoDB.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    name: str
    googleId: str


class UserCreate(UserBase):
    """Used internally when creating a new user from a Google login."""
    pass


class UserInDB(UserBase):
    """Full internal representation, including Mongo's _id."""
    id: str = Field(alias="_id")
    createdAt: datetime
    updatedAt: Optional[datetime] = None

    class Config:
        populate_by_name = True


class UserOut(BaseModel):
    """What we actually return to the frontend — no internal Mongo fields exposed."""
    id: str
    email: EmailStr
    name: str
    createdAt: datetime

    class Config:
        from_attributes = True