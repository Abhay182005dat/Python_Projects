from sqlalchemy.orm import Session
import models, schemas
from security import hash_password # custom library we made for making password hashes

def create_user(db : Session , email : str , password : str ):
    user = models.User(email = email , hashed_password = hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_todo(db : Session , todo : schemas.TodoCreate, user_id : str):
    new_todo = models.Todo(title = todo.title , user_id = user_id)
    db.add(new_todo)
    db.commit()          # save
    db.refresh(new_todo) # refresh to get id
    return new_todo

# read / get all todos 
def get_todos(db: Session , user_id : str):
    return db.query(models.Todo).filter(models.Todo.user_id == user_id)

# delete todo
def delete_todo(db: Session, todo_id: int , user_id = str):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id , models.Todo.user_id == user_id).first()  # .first() gives the first matching row
    if todo:
        db.delete(todo)
        db.commit()
    return todo


def update_todo_status(db : Session , todo_id : int , is_completed : bool , user_id : str):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id , models.Todo.user_id == user_id).first()
    if not todo:
        return None
    todo.is_completed = is_completed
    db.commit()
    db.refresh(todo)
    return todo