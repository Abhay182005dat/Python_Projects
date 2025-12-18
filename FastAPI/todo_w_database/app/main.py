from fastapi import FastAPI , APIRouter , Depends ,HTTPException
from database import engine , SessionLocal
import models , crud , schemas
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from jwt_utils import create_access_token , decode_access_token
from auth_dependency import get_current_user
from security import verify_password


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# router = APIRouter(   if you apply this then there is no need to put user_id : str = Depends(get_current_user)
#     dependencies=[Depends(get_current_user)]   in every important functions cause you are checking from the router itself
# )

router = APIRouter()
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db   # Give this database session to the route temporarily, and clean it up afterward.
    finally:
        db.close()


@router.get("/health")
def health():
    return {"status" : "OK"}



@app.get("/")
def home():
    return FileResponse("static/index.html")

@router.post('/login')
def login(form_data : OAuth2PasswordRequestForm = Depends() , db : Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not db_user:
        raise HTTPException(status_code=401 , detail = "Invalid credentials")
    
    if not verify_password(form_data.password , db_user.hashed_password):
        raise HTTPException(status_code=401 , detail="Invalid credentials")
    
    token = create_access_token(
        {"sub" : str(db_user.id)}
    )

    return {
        'access_token' : token,
        'token_type': "bearer"
    }


@router.post('/register')
def register(user : schemas.UserCreate, db : Session = Depends(get_db) ):

    existing = db.query(models.User).filter(models.User.email == user.email ).first()

    if existing:
        raise HTTPException(status_code=400 , detail="Email Already registered")
    
    new_user = crud.create_user(db , user.email , user.password)
    return {'message' : 'user registered successfully'}

@router.get('/protected')
def protected(user_id : str = Depends(get_current_user)):
    return {'message' : f"Hello user {user_id}"}




@router.get("/todos",response_model=list[schemas.TodoResponse])
def read_todos(user_id : str = Depends(get_current_user),db : Session = Depends(get_db)): # “FastAPI, before calling this function, run get_db() and put its result into db.”

    return crud.get_todos(db,user_id)
# Session is a typeholder which expects a session object 


@router.post("/todos" , response_model=schemas.TodoResponse)
def create_todo(todo : schemas.TodoCreate , user_id : str = Depends(get_current_user) , db : Session = Depends(get_db)):
    return crud.create_todo(db,todo , user_id)



@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int,user_id : str = Depends(get_current_user) ,db: Session = Depends(get_db)):
    todo = crud.delete_todo(db, todo_id , user_id)
    if not todo:
        raise HTTPException(status_code=403, detail="Not Allowed")
    return {"message": "Todo deleted"}


@router.put("/todos/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(todo_id: int, todo: schemas.TodoUpdate,
                user_id : str = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    
    updated = crud.update_todo_status(db, todo_id, todo.is_completed, user_id   )
    if not updated:
        raise HTTPException(status_code=403, detail="Not Allowed")
    return updated


@router.get("/test-token")
def test_token():
    token = create_access_token({'sub':'123'})
    return {'token' : token}


@router.get("/test-decode")
def test_decode(token : str):
    payload = decode_access_token(token)
    if payload is None:
        return {'Valid': False}
    return {
        'Valid' : True,
        'Payload' : payload

    }



app.include_router(router)