# load_balancer_least_connections.py

from fastapi import FastAPI
from typing import Dict

app = FastAPI()

# Track active connections per server
servers_connections = {
    "server1": 0,
    "server2": 0,
    "server3": 0,
    "server4": 0
}

def get_least_busy_server():
    # Step 1: Find server with LOWEST active connections
    least_busy = min(servers_connections, key=servers_connections.get)
    
    # Step 2: Increase connection count for that server
    servers_connections[least_busy] += 1
    
    # Step 3: Return that server
    return least_busy

def release_server_connection(server_name: str):
    # Step 1: Request finished, decrease connection count
    servers_connections[server_name] -= 1

@app.post("/todos")
def create_todo(title: str, description: str):
    # Step 1: Get server with least connections
    selected_server = get_least_busy_server()
    
    # Step 2: Send request to that server
    # response = requests.post(f"{selected_server}/todos", json={...})
    
    # Step 3: When done, release connection
    release_server_connection(selected_server)
    
    # Step 4: Return response
    return {
        "sent_to": selected_server, 
        "title": title,
        "server_loads": servers_connections
    }

@app.get("/todos")
def get_todos():
    # Step 1: Get least busy server
    selected_server = get_least_busy_server()
    
    # Step 2: Send request
    # response = requests.get(f"{selected_server}/todos")
    
    # Step 3: Release connection
    release_server_connection(selected_server)
    
    # Step 4: Return
    return {
        "sent_to": selected_server,
        "server_loads": servers_connections
    }

@app.get("/server-loads")
def check_loads():
    # Show how many connections each server has
    return servers_connections

# Example:
# Server1 has 5 connections (busy)
# Server2 has 2 connections (free)
# Server3 has 3 connections (medium)
# Server4 has 1 connection (free)
#
# New request arrives → Goes to Server4 (least busy with 1 connection)
# Server4 connections: 1 → 2

# Run: uvicorn load_balancer_least_connections.py:app --port 80