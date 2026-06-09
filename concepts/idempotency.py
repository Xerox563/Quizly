# IDEMPOTENCY KEYS
# What is Idempotency?

'''
# Idempotency means that if the same request is sent multiple times,
# the result should be the same as sending it only once.

# Simple idea:
# Same request sent many times
# → Action happens only once
# → No duplicate records

# Why Do We Need It?

# Example:
# User clicks "Create Todo"

# Request is sent
# ↓
# Network becomes slow
# ↓
# User thinks it failed
# ↓
# User clicks again

# Now the server receives the same request twice.

# Without Idempotency:

# Request 1 → Create Todo
# Request 2 → Create Todo

# Result:
# Two identical todos are created.
# Duplicate data appears.

# This is a problem.

# What is an Idempotency Key?

# An idempotency key is a unique identifier attached to a request.

# Think of it like a tracking number.

# Example:
# Request → Key = abc123

# The server remembers this key after processing the request.

# How Does It Work?

# First Request

# Request arrives with key = abc123

# Server checks:
# "Have I seen abc123 before?"

# Answer:
# No

# So the server:
# - Processes the request
# - Creates the todo
# - Stores the response
# - Saves key abc123

# Second Request (Retry)

# Due to network issues or user double-clicking,
# the same request arrives again.

# Key = abc123

# Server checks:
# "Have I seen abc123 before?"

# Answer:
# Yes

# Instead of processing again:
# - Server returns the previous response
# - No new todo is created

# Result:
# Only one todo exists.

# Why Is Idempotency Important?

# It prevents:
# - Duplicate todos
# - Duplicate payments
# - Duplicate money transfers
# - Duplicate bookings
# - Duplicate emails

# It protects against:
# - User double-clicks
# - Network retries
# - Timeouts
# - Application failures

# Without Idempotency:

# Same request
# → Processed multiple times
# → Duplicate actions occur

# With Idempotency:

# Same request
# → Recognized using the idempotency key
# → Processed only once

# Real-World Examples

# Payment Processing:
# User pays ₹100
# Request retried
# Without idempotency → Charged twice
# With idempotency → Charged once

# Money Transfer:
# Transfer ₹1000
# Request retried
# Without idempotency → ₹2000 transferred
# With idempotency → ₹1000 transferred once

# Appointment Booking:
# User books a slot
# Request retried
# Without idempotency → Two bookings created
# With idempotency → One booking created

# Email Sending:
# Request retried
# Without idempotency → Multiple emails sent
# With idempotency → Single email sent

# Interview Definition

# Idempotency is a mechanism that ensures
# the same request can be safely retried multiple times
# without creating duplicate actions.
# This is achieved using a unique idempotency key
# that helps the server identify previously processed requests.
'''

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import redis
import json
import uuid

DB_URL = "postgresql://user:password@localhost/todo_db"
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
cache = redis.Redis(host='localhost', port=6379)

Base = declarative_base()

class TodoDB(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    title = Column(String)

class TodoCreate(BaseModel):
    title: str

app = FastAPI()

@app.post("/todos")
def create_todo(
    user_id: int,
    todo: TodoCreate,
    idempotency_key: str = Header(None)  # Get from request header
):
    # Step 1: If no idempotency key, generate one
    if not idempotency_key:
        idempotency_key = str(uuid.uuid4())
    
    # Step 2: Check if we've seen this key before
    cache_key = f"idempotency:{idempotency_key}"
    cached_response = cache.get(cache_key)
    
    # Step 3: If cached, return immediately
    if cached_response:
        return json.loads(cached_response)
    
    # Step 4: Process request (create todo)
    db = Session()
    new_todo = TodoDB(user_id=user_id, title=todo.title)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    db.close()
    
    # Step 5: Create response
    response = {
        "id": new_todo.id,
        "title": new_todo.title,
        "idempotency_key": idempotency_key
    }
    
    # Step 6: Cache response for future identical requests
    # Keep cached for 24 hours
    cache.setex(cache_key, 86400, json.dumps(response))
    
    # Step 7: Return response
    return response

# For DELETE requests:

@app.delete("/todos/{todo_id}")
def delete_todo(
    todo_id: int,
    idempotency_key: str = Header(None)
):
    # Step 1: Check cache
    cache_key = f"idempotency:{idempotency_key}"
    cached = cache.get(cache_key)
    
    # Step 2: If cached, return cached response
    if cached:
        return json.loads(cached)
    
    # Step 3: Delete from database
    db = Session()
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if todo:
        db.delete(todo)
        db.commit()
    db.close()
    
    # Step 4: Cache response
    response = {"deleted": todo_id}
    cache.setex(cache_key, 86400, json.dumps(response))
    
    # Step 5: Return
    return response