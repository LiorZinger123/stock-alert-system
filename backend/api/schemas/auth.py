from pydantic import BaseModel, EmailStr


class Credentials(BaseModel):
    username: str
    password: str
    

class RegisterPayload(BaseModel):
    username: str
    password: str
    email: EmailStr
