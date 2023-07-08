from typing import Literal, List
from datetime import date
from re import fullmatch
from pydantic import BaseModel, EmailStr, validator

class Login(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    token: str

class UserBASE(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    handle: str
    phone: str
    gender: Literal['male', 'female']
    
    @validator('first_name')
    def first_name_verify(cls, v: str):
        assert v.isalpha(), 'First name should be alphabetic'
        return v
    
    @validator('last_name')
    def last_name_verify(cls, v: str):
        assert v.isalpha(), 'Last name should be alphabetic'
        return v

    @validator('handle')
    def handle_verify(cls, v: str):
        assert v.isalnum(), 'Handle should be alphanumeric'
        return v

    @validator('phone')
    def phone_verify(cls, v: str):
        assert fullmatch('[6-9][0-9]{9}',v) is not None, 'Invalid number'
        return v
    
class UserInsert(UserBASE):
    password: str

class User(UserBASE):
    id: str
    created_on: date
    following: List[str]
