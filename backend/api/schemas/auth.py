from pydantic import BaseModel, EmailStr, Field, field_validator


class Credentials(BaseModel):
    username: str
    password: str
    

class RegisterPayload(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator('password')
    def password_must_contain_rules(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v
