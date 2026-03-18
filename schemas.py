from pydantic import BaseModel
from typing import List, Optional

# Shared properties
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    id: int
    password: Optional[str] = None
    email: Optional[str] = None

class UserInDBBase(UserBase):
    id: int

    class Config:
        from_attributes = True # Changed from orm_mode = True for Pydantic v2

class User(UserInDBBase):
    pass

# Shared properties for Post
class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    title: Optional[str] = None
    content: Optional[str] = None

class PostInDBBase(PostBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True # Changed from orm_mode = True for Pydantic v2

class Post(PostInDBBase):
    owner: UserInDBBase # Include owner information

# Relationship models (optional, for response models that include relationships)
class UserWithPosts(UserInDBBase):
    posts: List[PostInDBBase] = []

    class Config:
        from_attributes = True # Changed from orm_mode = True for Pydantic v2
