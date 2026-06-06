from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime
import uvicorn

# Database setup
DATABASE_URL = "postgresql://todo:admin@localhost/todo_db"
engine = create_engine(DATABASE_URL) # SQLAlchemy, connect to PostgreSQL using this URL.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # creates db sessions, whenever we need the db access we use SessionLocal
Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database model
class TodoDB(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine) # checks does table todos exist ?

# Pydantic model for request/response
class TodoCreate(BaseModel):
    title: str
    description: str

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Allows FastAPI to convert SQLAlchemy objects into JSON automatically.

app = FastAPI()

# Endpoint to add todo
@app.post("/todos", response_model=TodoResponse)
def create_todo(
    todo: TodoCreate,
    db: Session = Depends(get_db)
): # FastAPI: Receives request data, Converts it into TodoCreate, Opens database session.

    # Creates todo in database
    new_todo = TodoDB(title=todo.title, description=todo.description)
    db.add(new_todo)
    db.commit() # this basically inserts into tables
    db.refresh(new_todo) # fetches generated values
    return new_todo

# Endpoint to fetch all todos
@app.get("/todos", response_model=list[TodoResponse])
def get_todos(
    db: Session = Depends(get_db)
):
    # Fetches all todos from database
    todos = db.query(TodoDB).all()
    return todos

# Endpoint to delete todo
@app.delete("/todos/{todo_id}")
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    # Finds and deletes todo by id
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo)
    db.commit()

    return {"message": "Todo deleted"}

if __name__ == "__main__":
    uvicorn.run(
        "todo_basic:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

# Why do we need Depends(get_db)?
# Think of get_db() as a database connection provider:
'''
- db: Session = Depends(get_db) tells FastAPI:
- For every request, create a fresh database session, give it to this function, and automatically close it when the request finishes.

Request
   ↓
get_db()
   ↓
Open DB Session
   ↓
Route Function
   ↓
Close DB Session
'''    

# Without Depends(get_db), using:db: Session = SessionLocal()
# creates the session incorrectly and may leave database connections open. Depends(get_db) is the FastAPI-recommended way because it safely manages the database connection for every request.