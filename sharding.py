from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Shard 1: Users 1-250k
SHARD_1 = "postgresql://user:password@shard-1:5432/todo_db"
engine_1 = create_engine(SHARD_1)
Session_1 = sessionmaker(bind=engine_1)

# Shard 2: Users 250k-500k
SHARD_2 = "postgresql://user:password@shard-2:5432/todo_db"
engine_2 = create_engine(SHARD_2)
Session_2 = sessionmaker(bind=engine_2)

# Shard 3: Users 500k-750k
SHARD_3 = "postgresql://user:password@shard-3:5432/todo_db"
engine_3 = create_engine(SHARD_3)
Session_3 = sessionmaker(bind=engine_3)

# Shard 4: Users 750k-1m
SHARD_4 = "postgresql://user:password@shard-4:5432/todo_db"
engine_4 = create_engine(SHARD_4)
Session_4 = sessionmaker(bind=engine_4)

shards = [Session_1, Session_2, Session_3, Session_4]

Base = declarative_base()

class TodoDB(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    title = Column(String)

# Create table in all 4 shards
for session_maker in shards:
    engine = session_maker.kw['bind']
    Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_shard(user_id: int):
    # Step 1: Determine which shard this user belongs to
    shard_number = user_id % 4  # user_id mod 4 = shard number
    # Step 2: Return that shard's database
    return shards[shard_number]()

@app.post("/todos")
def create_todo(user_id: int, title: str):
    # Step 1: Calculate which shard this user is in
    db = get_shard(user_id)
    # Step 2: Save to that shard ONLY (not all shards)
    todo = TodoDB(user_id=user_id, title=title)
    db.add(todo)
    db.commit()
    db.close()
    # Step 3: Other shards don't know about this todo
    return {"id": todo.id}

@app.get("/todos/{user_id}")
def get_todos(user_id: int):
    # Step 1: Find which shard this user is in
    db = get_shard(user_id)
    # Step 2: Query ONLY that shard (250 million rows, not 1 billion)
    todos = db.query(TodoDB).filter(TodoDB.user_id == user_id).all()
    db.close()
    # Step 3: Fast query because shard is small
    return todos

# BENEFIT:
# Before: 1 database with 1 billion rows
# After: 4 databases with 250 million rows each
# Query is 4x faster!
# Storage is split across 4 machines