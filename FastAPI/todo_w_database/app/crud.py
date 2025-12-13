from sqlalchemy.orm import Session
import models, schemas


def create_todo(db : Session , todo : schemas.TodoCreate):
    new_todo = models.Todo(title = todo.title)
    db.add(new_todo)
    db.commit()          # save
    db.refresh(new_todo) # refresh to get id
    return new_todo

# read / get all todos 
def get_todos(db: Session):
    return db.query(models.Todo).all()

# delete todo
def delete_todo(db: Session, todo_id: int):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()  # .first() gives the first matching row
    if todo:
        db.delete(todo)
        db.commit()
    return todo


def update_todo_status(db : Session , todo_id : int , is_completed : bool):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        return None
    todo.is_completed = is_completed
    db.commit()
    db.refresh(todo)
    return todo