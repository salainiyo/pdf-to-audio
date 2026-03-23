import re
from sqlmodel import Field, SQLModel
from pydantic import EmailStr, field_validator, BaseModel

class UserBase(SQLModel):
    email:EmailStr = Field(unique=True, index=True)

class User(UserBase, table=True):
    id: int|None = Field(default=None, primary_key=True)
    password_hash: str

class UserCreate(UserBase):
    password: str
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long.')
        if not re.search(r"[A-Z]", v):
            raise ValueError('Password must contain at least one uppercase letter.')
        if not re.search(r"[a-z]", v):
            raise ValueError('Password must contain at least one lowercase letter.')
        if not re.search(r"\d", v):
            raise ValueError('Password must contain at least one number.')
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError('Password must contain at least one special character.')
        return v

class UserRead(SQLModel):
    id: int|None
    email: str

class LogoutRequest(BaseModel):
    refresh_token : str

    
class AccessTokenBlocklist(SQLModel, table=True):
    id: int|None = Field(default=None, primary_key=True)
    token: str = Field(index=True)
    token_type: str = Field(index=True)
    

class RefreshTokenBlocklist(SQLModel, table=True):
    id: int|None = Field(default=None, primary_key=True)
    token: str = Field(index=True)
    token_type: str = Field(index=True)

class TokensRead(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"