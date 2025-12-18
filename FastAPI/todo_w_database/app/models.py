from database import Base
from sqlalchemy import Column, Integer, String, Boolean

class Todo(Base):
    __tablename__ = 'todos' # “SQLAlchemy, please create/use a table named todos for this class.”

    id = Column(Integer,primary_key=True,index=True)
    title = Column(String, nullable=False)
    is_completed = Column(Boolean , default=False)
    user_id = Column(String , nullable=False)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer , primary_key=True , index = True)
    email = Column(String , unique=True , nullable=False)
    hashed_password = Column(String , nullable = False)
    