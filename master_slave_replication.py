from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

# MASTER DATABASE (for writes only)
MASTER_DB = "postgresql://user:password@master-db:5432/todo_db"
master_engine = create_engine(MASTER_DB)
MasterSessionLocal = sessionmaker(bind=master_engine)

# SLAVE DATABASES (for reads only) - can have multiple
SLAVE_DB_1 = "postgresql://user:password@slave-db-1:5432/todo_db"
SLAVE_DB_2 = "postgresql://user:password@slave-db-2:5432/todo_db"
slave_engine_1 = create_engine(SLAVE_DB_1)
slave_engine_2 = create_engine(SLAVE_DB_2)
SlaveSessionLocal_1 = sessionmaker(bind=slave_engine_1)
SlaveSessionLocal_2 = sessionmaker(bind=slave_engine_2)

slave_sessions = [SlaveSessionLocal_1, SlaveSessionLocal_2]
slave_index = 0

Base = declarative_base()

class TodoDB(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=master_engine)

class TodoCreate(BaseModel):
    title: str
    description: str

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    class Config:
        from_attributes = True

app = FastAPI()

def get_slave_session():
    # Step 1: Load balance across slave databases
    global slave_index
    selected_slave = slave_sessions[slave_index % len(slave_sessions)]
    slave_index += 1
    # Step 2: Return slave session
    return selected_slave()

@app.post("/todos", response_model=TodoResponse)
def create_todo(todo: TodoCreate):
    # Step 1: WRITE goes to MASTER only
    db = MasterSessionLocal()
    new_todo = TodoDB(title=todo.title, description=todo.description)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    # Step 2: Master sends changes to slaves automatically (replication lag: 1-5 seconds)
    db.close()
    return new_todo

@app.get("/todos", response_model=list[TodoResponse])
def get_todos():
    # Step 1: READ from SLAVE (not master)
    # Slaves have copy of data, master is free for writes
    db = get_slave_session()
    todos = db.query(TodoDB).all()
    db.close()
    # Step 2: Return todos
    return todos

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    # Step 1: WRITE goes to MASTER
    db = MasterSessionLocal()
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if not todo:
        db.close()
        return {"error": "Not found"}
    db.delete(todo)
    db.commit()
    # Step 2: Master sends delete to slaves (replication lag)
    db.close()
    return {"deleted": todo_id}

# HOW IT WORKS:
# 
# Master (Write):        Slave-1 (Read):      Slave-2 (Read):
# Step 1: Receive write   (copies data)        (copies data)
# Step 2: Process write   Wait 1-5 sec         Wait 1-5 sec
# Step 3: Save to disk    Get sync'd copy      Get sync'd copy
# Step 4: Send to slaves  Ready for reads      Ready for reads
#
# If 1000 users create todos:
# - All writes go to 1 master (100 writes/sec)
# - All reads go to 2 slaves (400 reads/sec each = 800 total)
# - Master free to handle more writes