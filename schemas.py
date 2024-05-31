from pydantic import BaseModel
from typing import List

class Blog(BaseModel):
    title : str
    body : str
    # id : int
    class Config:
        orm_mode = True


class ShowBlog(Blog):
    creator : 'ShowUsers'



class Users(BaseModel):
    name : str
    email : str
    password : str


class ShowUsers(BaseModel):
    name : str
    email : str
    id : int
    blogs : List[Blog] =[]

    class Config:
        orm_mode = True


class Login(BaseModel):
    username : str
    password : str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None