# Bulk Operation
# Bulk operations mean processing many records together as a group instead of handling them one by one.
# Used in Data import , Data migration, batch processing

# Why are they used?
'''
1. Better Performance

If you process records one by one, the system has to repeat the same work again and again. Bulk operations reduce this repeated work and make processing much faster.

2. Fewer Database Requests

Without bulk operations, the application keeps talking to the database repeatedly for every record. With bulk operations, it sends everything together, reducing communication.

--------- Without Bulk ---------
# 1000 todos to create
for i in range(1000):
    create_todo(f"Todo {i}")
    
# 1000 API calls
# 1000 database connections
# 1000 disk writes
# Takes 10 minutes!
---------

--------- With Bulk ---------
# Create 1000 todos in 1 API call
create_todos_bulk([
    "Todo 1",
    "Todo 2",
    ...
    "Todo 1000"
])

# 1 API call
# 1 database connection
# 1 disk write (batch)
# Takes 5 seconds!

200x faster!
---------
3. Lower Database Load

When thousands of separate operations are performed, the database has to handle each one individually. Bulk operations reduce the workload and help the database perform more efficiently.

4. Reduced Network Traffic

Each interaction between the application and database travels over a network. Bulk operations reduce the number of trips, saving time and resources.

5. Better Resource Usage

Databases are optimized to process groups of records together. Bulk operations allow them to use CPU and memory more efficiently.
'''
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List

DB_URL = "postgresql://user:password@localhost/todo_db"
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class TodoDB(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    title = Column(String)

class TodoCreate(BaseModel):
    user_id: int
    title: str

app = FastAPI()

# BULK CREATE
@app.post("/todos/bulk")
def create_todos_bulk(todos: List[TodoCreate]):
    # Step 1: Creatingg all todo objects
    todo_objects = [
        TodoDB(user_id=t.user_id, title=t.title)
        for t in todos
    ]
    
    # Step 2: Adding all at once
    db = Session()
    db.add_all(todo_objects)
    # Step 3: Commit once (not per todo)
    db.commit() 
    db.close()
    
    # Step 4: Return success
    return {
        "created": len(todos),
        "message": f"Created {len(todos)} todos"
    }

# BULK DELETE
@app.delete("/todos/bulk/old")
def delete_old_todos():
    # Step 1: Find all todos older than 30 days
    db = Session()
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Step 2: Delete all at once (not one by one)
    deleted_count = db.query(TodoDB).filter(
        TodoDB.created_at < thirty_days_ago
    ).delete()
    
    # Step 3: Commit once
    db.commit()
    db.close()
    
    # Step 4: Return
    return {
        "deleted": deleted_count,
        "message": f"Deleted {deleted_count} old todos"
    }

# BULK UPDATE
@app.put("/todos/bulk/complete")
def mark_todos_complete(user_id: int):
    # Step 1: Update all todos for user
    db = Session()
    
    # Step 2: Update all at once
    updated_count = db.query(TodoDB).filter(
        TodoDB.user_id == user_id,
        TodoDB.completed == False
    ).update({"completed": True})
    
    # Step 3: Commit once
    db.commit()
    db.close()
    
    # Step 4: Return
    return {
        "updated": updated_count,
        "message": f"Marked {updated_count} todos complete"
    }
