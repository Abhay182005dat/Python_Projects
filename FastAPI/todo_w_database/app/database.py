from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./todo.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
# Think of engine like:
# A phone line to the database
# It knows:
#     Which database (SQLite)
#     Where it lives (todo.db)
#     It does not run queries itself
#     It just knows how to connect

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
# Think of Session like:

#     A chat session with the database
#     You open a session
#     You ask questions (SELECT, INSERT)
#     You close the session
# sessionmaker is:
#     A factory that creates sessions

Base = declarative_base()   # a template for database tables

