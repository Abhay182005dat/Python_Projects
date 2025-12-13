from pydantic import BaseModel

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


# FastAPI returns SQLAlchemy objects
# Pydantic needs permission to read them
# orm_mode = True enables that