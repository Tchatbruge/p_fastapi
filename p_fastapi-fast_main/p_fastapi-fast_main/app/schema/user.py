from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    id: str
    username: str
    email: EmailStr
    password: str

