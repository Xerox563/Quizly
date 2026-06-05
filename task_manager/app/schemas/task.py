from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
    description: str
    priority: str


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: str
    status: str

# This file validates incoming data     