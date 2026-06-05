from fastapi import FastAPI

# Scheduler functions
from app.scheduler import (
    start_scheduler,
    stop_scheduler
)

# Fake database
from app.data.dummy_tasks import DUMMY_TASKS

# Request schema
from app.schemas.task import TaskCreate

# Background jobs
from app.celery_app import (
    send_email,
    generate_report
)

# CREATE FASTAPI APP
app =  FastAPI(
    title"Task Manager API",
    version"1.0.0"
)
 
# STARTUP EVENT

@app.on_event("startup")
async def startup():

    print("Application Starting...")

    # Start APScheduler
    start_scheduler()

    print("Scheduler Started")


# SHUTDOWN EVENT

@app.on_event("shutdown")
async def shutdown():

    print("Application Stopping...")

    stop_scheduler()

    print("Scheduler Stopped")


# ROOT ROUTE

@app.get("/")
def home():

    return {
        "message": "Task Manager API Running"
    }


# GET ALL TASKS

@app.get("/tasks")
def get_tasks():

    return {
        "total": len(DUMMY_TASKS),
        "tasks": DUMMY_TASKS
    }

 
# GET SINGLE TASK

@app.get("/tasks/{task_id}")
def get_task(task_id: int):

    task =  [ task for task in DUMMY_TASKS if task["id"] == task_id ]
    return task  

# CREATE TASK

@app.post("/tasks")
def create_task(task: TaskCreate):

    new_task = {
        "id": len(DUMMY_TASKS) + 1,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "status": "pending",
        "completed": False
    }

    # Save into fake database
    DUMMY_TASKS.append(new_task)

    # Background Email Job

    send_email.delay(
        "user@example.com",
        f"Task Created: {task.title}"
    )

    return {
        "message": "Task Created Successfully",
        "task": new_task
    }



# GENERATE REPORT

@app.post("/tasks/{task_id}/report")
def create_report(task_id: int):

    # Queue report generation

    generate_report.delay(task_id)

    return {
        "status": "queued",
        "message": "Report generation started",
        "task_id": task_id
    }


# HEALTH CHECK

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }