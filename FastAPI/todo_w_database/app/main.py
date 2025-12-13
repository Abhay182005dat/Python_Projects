from fastapi import FastAPI , APIRouter , Depends ,HTTPException
from database import engine , SessionLocal
import models , crud , schemas
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

router = APIRouter()
models.Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return FileResponse("static/index.html")



def get_db():
    db = SessionLocal()
    try:
        yield db   # Give this database session to the route temporarily, and clean it up afterward.
    finally:
        db.close()


@router.get("/health")
def health():
    return {"status" : "OK"}


@router.get("/todos",response_model=list[schemas.TodoResponse])
def read_todos(db : Session = Depends(get_db)): #“FastAPI, before calling this function, run get_db() and put its result into db.”
    return crud.get_todos(db)
# Session is a typeholder which expects a session object 


@router.post("/todos" , response_model=schemas.TodoResponse)
def create_todo(todo : schemas.TodoCreate , db : Session = Depends(get_db)):
    return crud.create_todo(db,todo)



@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int,db: Session = Depends(get_db)):
    todo = crud.delete_todo(db, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted"}


@router.put("/todos/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(todo_id: int, todo: schemas.TodoUpdate, db: Session = Depends(get_db)):
    updated = crud.update_todo_status(db, todo_id, todo.is_completed)
    if not updated:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated


app.include_router(router)