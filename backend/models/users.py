from sqlmodel import Field, SQLModel

class UserBase(SQLModel):
    email:str = Field(unique=True, index=True)

class User(UserBase, table=True):
    id: int|None = Field(default=None, primary_key=True)
    password_hash: str

class UserCreate(UserBase):
    password: str

class UserRead(SQLModel):
    id: int|None
    email: str