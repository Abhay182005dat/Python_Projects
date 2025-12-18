from pydantic import BaseModel , EmailStr, field_validator

class TodoCreate(BaseModel):
    title : str

class TodoResponse(BaseModel):
    id : int
    title : str
    is_completed : bool

    class Config:
        orm_mode = True # to allow sqlalchemy models

class TodoUpdate(BaseModel):
    is_completed : bool

class UserCreate(BaseModel):
    email : EmailStr
    password : str

    @field_validator("password")      # for errors in passwords lengths
    @classmethod
    def password_length(cls, v):
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password too long (max 72 bytes)")
        return v

# FastAPI returns SQLAlchemy objects
# Pydantic needs permission to read them
# orm_mode = True enables that