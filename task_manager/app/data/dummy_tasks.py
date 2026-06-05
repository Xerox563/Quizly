from datetime import datetime

DUMMY_TASKS = [
    {
        "id": i,
        "title": f"Task {i}",
        "description": f"Description {i}",
        "status": ["pending", "in_progress", "completed"][i % 3],
        "priority": ["low", "medium", "high"][i % 3],
        "created_at": datetime.now(),
        "completed": False
    }
    for i in range(1, 21)
]