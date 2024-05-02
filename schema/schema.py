from pydantic import BaseModel, EmailStr
from typing import List

class UserCreateSchema(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str

    class Config:
        from_attribute = True

class UserUpdateSchema(BaseModel):
    name: str
    surname: str
    email: EmailStr
    height : float
    weight : int

    class Config:
        from_attribute = True



#-------------- schema Dexter 

class ActivitySchema(BaseModel):
    name:str
    description: str 
    time:str
    category:str

    class Config:
        from_attribute = True 

class ActivityResponseSchema(BaseModel):
    id: int
    name: str 
    description: str 
    time: str
    category:str

    
    class Config:
        from_attribute = True 



