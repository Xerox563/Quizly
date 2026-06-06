# load_balancer_round_robin.py

from fastapi import FastAPI
from typing import List

app = FastAPI()

# List of backend servers (our 4 todo servers)
servers = [
    "http://server1:8001",
    "http://server2:8002", 
    "http://server3:8003",
    "http://server4:8004"
]

current_server_index = 0  # Track which server was last used

def get_next_server():
    # Round-robin: cycle through servers in order
    global current_server_index
    
    # Get server at current index
    server = servers[current_server_index]
    
    # Move to next server for next request
    current_server_index = (current_server_index + 1) % len(servers)
    
    # Return current server
    return server

@app.post("/todos")
def create_todo(title: str, description: str):
    # Step 1: Get next server using round-robin
    next_server = get_next_server()
    # Step 2: Send request to that server
    # response = requests.post(f"{next_server}/todos", json={...})
    # Step 3: Return response
    return {"sent_to": next_server, "title": title, "description": description}

@app.get("/todos")
def get_todos():
    # Step 1: Get next server
    next_server = get_next_server()
    # Step 2: Send request to that server
    # response = requests.get(f"{next_server}/todos")
    # Step 3: Return response
    return {"sent_to": next_server}

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    # Step 1: Get next server
    next_server = get_next_server()
    # Step 2: Send request to that server
    # response = requests.delete(f"{next_server}/todos/{todo_id}")
    # Step 3: Return response
    return {"sent_to": next_server, "deleted": todo_id}

# Example requests:
# Request 1: /todos POST → Server 1
# Request 2: /todos GET → Server 2
# Request 3: /todos DELETE → Server 3
# Request 4: /todos POST → Server 4
# Request 5: /todos GET → Server 1 (loops back)

# Run: uvicorn load_balancer_round_robin.py:app --port 80